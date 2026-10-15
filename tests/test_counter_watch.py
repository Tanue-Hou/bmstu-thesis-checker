"""Hardware observations must be bound to real loader/write/report events."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from native_reference_cli import validate_counter_watch,validate_native_run
BASE=ROOT/'evidence/business-map-232/first-indent-watch-native-r1'


class CounterWatchTests(unittest.TestCase):
    def trace(self,case='negativeLeft_positive_writer_control'):
        return json.loads((BASE/case/'trace.json').read_text())

    def test_all_six_actual_native_observations_and_positive_writer(self):
        receipt=json.loads((BASE/'receipt.json').read_text())
        self.assertEqual(len(receipt['cases']),6)
        for row in receipt['cases']:
            with self.subTest(case=row['case']):
                trace=self.trace(row['case'])
                text=(BASE/row['case']/'native-result.txt').read_bytes().decode('utf-8')
                self.assertEqual(len(validate_native_run(trace,text,row['mode'],row['format'],row['source_sha256'],True)),row['native_diagnostic_count'])
                observed=validate_counter_watch(trace)
                self.assertEqual(observed['final_values'],row['watch']['final_values'])
                self.assertEqual(observed['changed_events']['first'],0)
        positive=validate_counter_watch(self.trace())
        self.assertEqual(positive['final_values']['left'],1)
        self.assertEqual(positive['changed_events']['left'],1)

    def test_same_value_clearing_writes_are_valid_observations(self):
        trace=self.trace('noFirst')
        self.assertTrue(all(w['before']==w['after'] for w in trace['first_indent_counter_watch']['writes']))
        self.assertEqual(validate_counter_watch(trace)['write_events'],2)

    def test_dropped_debug_write_cannot_leave_accepted_summary(self):
        trace=self.trace()
        trace['events']=[e for e in trace['events'] if 'counter_write' not in e]
        with self.assertRaisesRegex(ValueError,'summary does not match'):
            validate_counter_watch(trace)

    def test_wrong_watch_length_mask_is_rejected(self):
        trace=self.trace()
        trace['first_indent_counter_watch']['observed_debug']['Dr7']='0x550005'
        with self.assertRaisesRegex(ValueError,'four-byte write watch'):
            validate_counter_watch(trace)

    def test_report_alias_and_incomplete_interval_are_rejected(self):
        for change in ['wrong_base','active','not_disarmed']:
            trace=self.trace();watch=trace['first_indent_counter_watch']
            if change=='wrong_base':watch['report_base']+=4
            elif change=='active':watch['active']=True
            else:watch['disarmed']=False
            with self.subTest(change=change),self.assertRaises(ValueError):
                validate_counter_watch(trace)

    def test_foreign_event_thread_is_rejected(self):
        trace=self.trace()
        next(e for e in trace['events'] if 'counter_write' in e)['tid']+=1
        with self.assertRaisesRegex(ValueError,'ownership'):
            validate_counter_watch(trace)

    def test_unobserved_counter_change_is_rejected(self):
        trace=self.trace()
        trace['first_indent_counter_watch']['final_values']['first']=1
        with self.assertRaisesRegex(ValueError,'Final counter values'):
            validate_counter_watch(trace)

    def test_reordered_interval_is_rejected(self):
        trace=self.trace()
        events=trace['events']
        start=next(i for i,e in enumerate(events) if e.get('hit')=='docx_load')
        end=next(i for i,e in enumerate(events) if e.get('hit')=='paragraph_first_report_gate')
        events[start],events[end]=events[end],events[start]
        with self.assertRaisesRegex(ValueError,'reordered'):
            validate_counter_watch(trace)


if __name__=='__main__':unittest.main()
