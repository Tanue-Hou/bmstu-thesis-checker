"""Measured native232 drawing arithmetic and bounded VML textbox extraction."""
import math,re,struct
V='urn:schemas-microsoft-com:vml';W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
EMU_TO_MM=f32(1/36000)
NATIVE_VML_FACTORS={'':1.0,'mm':1.0,'cm':10.0,'pt':f32(25.4/72),'in':f32(25.4),'pc':f32(25.4/6),'px':f32(0.00276)}
def native_extent(cx,cy):
 try:
  width=f32(f32(int(cx))*EMU_TO_MM);height=f32(f32(int(cy))*EMU_TO_MM);area=f32(width*height)
  return (width,height,area) if all(math.isfinite(v) and v>0 for v in [width,height,area]) else (None,None,None)
 except (TypeError,ValueError,OverflowError):return None,None,None
def vml_textboxes(root):
 records=[]
 sizes=root.findall('.//{'+W+'}sectPr/{'+W+'}pgSz')
 try:
  page_width_mm=int(sizes[0].get('{'+W+'}w'))*25.4/1440 if len(sizes)==1 else None
  page_height_mm=int(sizes[0].get('{'+W+'}h'))*25.4/1440 if len(sizes)==1 else None
 except (ValueError,TypeError):page_width_mm=page_height_mm=None
 a4_profile=page_width_mm is not None and page_height_mm is not None and all(abs(v-target)<0.02 for v,target in zip(sorted([page_width_mm,page_height_mm]),[210,297]))
 width_base,height_base=((172.0,259.0) if page_width_mm<230 else (259.0,172.0)) if page_width_mm is not None else (None,None)
 for shape in root.findall('.//{'+V+'}shape'):
  textbox=shape.find('{'+V+'}textbox')
  if textbox is None:continue
  style={key.strip().lower():value.strip().lower() for piece in shape.get('style','').split(';') if ':' in piece for key,value in [piece.split(':',1)]}
  def mm(value):
   match=re.fullmatch(r'([+]?(?:\d+(?:\.\d*)?|\.\d+))(mm|cm|pt|in|pc|px)?',value or '')
   if not match:return None
   try:
    number=f32(f32(float(match[1]))*NATIVE_VML_FACTORS[match[2] or '']);return number if math.isfinite(number) and number>0 else None
   except (ValueError,OverflowError):return None
  width,height=mm(style.get('width')),mm(style.get('height'));paragraphs=textbox.findall('.//{'+W+'}p');text=''.join(textbox.itertext())
  autofit=style.get('mso-fit-shape-to-text') in {'t','true'}
  effective_height=10.0 if autofit else height
  # The measured native build ignores the textbox-layer fit value on this path.
  textbox_style=textbox.get('style','')
  supported=(width is not None and height is not None and max(width,height)<=50 and not any(style.get(k,'').endswith(('pc','px')) for k in ['width','height']) and shape.get('type')=='#_x0000_t202' and set(shape.attrib)<={'id','type','style'} and set(textbox.attrib)<={'style','inset'} and textbox_style in {'','mso-fit-shape-to-text:t','mso-fit-shape-to-text:true','mso-fit-shape-to-text:f','mso-fit-shape-to-text:false'} and textbox.get('inset') in {None,'0,0,0,0','2mm,2mm,2mm,2mm'} and style.get('mso-fit-shape-to-text') in {None,'t','true','f','false'} and style.get('position')=='absolute' and set(style)<={'position','width','height','margin-left','margin-top','mso-fit-shape-to-text'} and style.get('margin-left')=='0' and style.get('margin-top')=='0' and len(paragraphs)==1 and len(paragraphs[0])==1 and len(paragraphs[0][0])==1 and paragraphs[0][0][0].tag=='{'+W+'}t' and shape.getparent().tag=='{'+W+'}pict')
  overflow=(width>width_base+5 or effective_height>height_base-5) if width is not None and effective_height is not None and width_base is not None else None
  left=0.0 if re.fullmatch(r'[+]?0(?:\.0+)?(?:mm|cm|pt|in)?',style.get('margin-left','')) else mm(style.get('margin-left'));top=0.0 if re.fullmatch(r'[+]?0(?:\.0+)?(?:mm|cm|pt|in)?',style.get('margin-top','')) else mm(style.get('margin-top'))
  position_inside=(0<=left<=width_base and 0<=top<=height_base) if left is not None and top is not None and width_base is not None else None
  # Larger dimensions use the same syntax guards; only the separately audited
  # bounds profile can gain verification, and only for the tested mm geometry.
  bounds_supported=(width is not None and height is not None and max(width,height)<=300 and width_base is not None and shape.get('type')=='#_x0000_t202' and set(shape.attrib)<={'id','type','style'} and not textbox.attrib and style.get('position')=='absolute' and set(style)<={'position','width','height','margin-left','margin-top'} and style.get('margin-left')=='0' and style.get('margin-top')=='0' and all(style.get(k,'').endswith('mm') for k in ['width','height']) and len(paragraphs)==1 and len(paragraphs[0])==1 and len(paragraphs[0][0])==1 and paragraphs[0][0][0].tag=='{'+W+'}t' and shape.getparent().tag=='{'+W+'}pict')
  records.append({'index':len(records),'xml_path':shape.getroottree().getpath(shape),'shape_id':shape.get('id'),'width_mm':width,'height_mm':height,'native_effective_height_mm':effective_height,'native_shape_autofit':autofit,'native_width_limit_mm':width_base+5 if width_base is not None else None,'native_height_limit_mm':height_base-5 if height_base is not None else None,'native_position_inside_bounds':position_inside,'bounds_geometry_supported':bounds_supported and a4_profile,'overflow_geometry_candidate':overflow,'dimension_measurement':'native232 VML conversion; px factor differs from screen pixels','position':style.get('position'),'text':text,'geometry_supported':supported and width_base is not None,'small_geometry_candidate':width is not None and height is not None and overflow is not True and (width<2 or (height<2 and not autofit))})
 return records
