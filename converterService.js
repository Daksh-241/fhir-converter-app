const { parse } = require('json2csv');

function convertBundleToCsv(fhirBundle) {
  if (!fhirBundle || !fhirBundle.entry) {
    return '';
  }

  const flattenedData = fhirBundle.entry.map(entry => {
    const resource = entry.resource;
    return {
      resourceType: resource.resourceType,
      id: resource.id,
      status: resource.status,
      code_text: resource.code?.text || resource.type?.[0]?.coding?.[0]?.display,
      effective_date: resource.effectiveDateTime || resource.onsetDateTime || resource.date,
      patient_reference: resource.subject?.reference || resource.patient?.reference
    };
  });

  const fields = ['resourceType', 'id', 'status', 'code_text', 'effective_date', 'patient_reference'];
  return parse(flattenedData, { fields });
}

module.exports = { convertBundleToCsv };
