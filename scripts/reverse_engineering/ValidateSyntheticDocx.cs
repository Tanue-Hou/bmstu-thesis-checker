// Read-only package/schema validation. Rendering and school compliance are separate.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web.Script.Serialization;
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Validation;

class ValidateSyntheticDocx {
    static int Main(string[] args) {
        var rows = new List<object>();
        foreach (string path in args) {
            using (var document = WordprocessingDocument.Open(path, false)) {
                var validator = new OpenXmlValidator(FileFormatVersions.Office2013);
                validator.MaxNumberOfErrors = 0;
                var errors = validator.Validate(document).Select(error => new {
                    id = error.Id, kind = error.ErrorType.ToString(),
                    description = error.Description,
                    part = error.Part == null ? null : error.Part.Uri.ToString(),
                    xpath = error.Path == null ? null : error.Path.XPath
                }).ToList();
                rows.Add(new {file = path, errors = errors, error_count = errors.Count});
            }
        }
        var serializer = new JavaScriptSerializer();
        serializer.MaxJsonLength = Int32.MaxValue;
        Console.OutputEncoding = new System.Text.UTF8Encoding(false);
        Console.WriteLine(serializer.Serialize(new {
            sdk = typeof(OpenXmlValidator).Assembly.FullName,
            target = "Office2013", read_only = true, cases = rows,
            limits = "SDK package/schema validation only; not rendering, school compliance or TestVkr equivalence."
        }));
        return 0;
    }
}
