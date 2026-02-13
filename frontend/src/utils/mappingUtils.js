/**
 * Automatically detects potential data mappings between two nodes based on their schemas.
 * @param {Object} sourceNode - The source node (where data comes from)
 * @param {Object} targetNode - The target node (where data goes to)
 * @returns {Array} List of detected mappings
 */
export function detectMappings(sourceNode, targetNode) {
    const mappings = []
    const sourceData = sourceNode.data
    const targetData = targetNode.data

    if (!sourceData || !targetData) return mappings

    // 1. Get all potential source fields from response schemas
    const responses = sourceData.responses || {}
    const successCode = Object.keys(responses).find(code => code.startsWith('2'))
    const sourceSchema = responses[successCode]?.content?.['application/json']?.schema

    if (!sourceSchema || !sourceSchema.properties) return mappings

    const sourceFields = []

    // Extraction helper to find fields at the top level and inside common wrappers
    function extractFields(schema, prefix = 'response') {
        if (!schema || !schema.properties) return
        Object.keys(schema.properties).forEach(key => {
            const path = `${prefix}.${key}`
            sourceFields.push({ name: key, path })

            // Only recurse into 'detail' and 'data' to keep suggestions clean but useful
            if ((key === 'detail' || key === 'data') && schema.properties[key].properties) {
                extractFields(schema.properties[key], path)
            }
        })
    }

    extractFields(sourceSchema)

    // 2. Get all required target fields (path parameters, query parameters, body properties)
    const targetParams = targetData.parameters || []
    const targetBodySpec = targetData.requestBodySpec?.content?.['application/json']?.schema

    // Check Path Parameters
    targetParams.filter(p => p.in === 'path').forEach(p => {
        // Try to find a match in source fields
        const match = findBestMatch(p.name, sourceFields)
        if (match) {
            mappings.push({ from: match.path, to: `pathParams.${p.name}` })
        }
    })

    // Check Body Properties (Optional: could be very complex, start simple)
    if (targetBodySpec && targetBodySpec.properties) {
        Object.keys(targetBodySpec.properties).forEach(key => {
            const match = findBestMatch(key, sourceFields)
            if (match) {
                // Only map if it's likely a shared ID or name
                const isId = key.toLowerCase().includes('id') || key.toLowerCase().includes('pk')
                if (isId) {
                    mappings.push({ from: match.path, to: key })
                }
            }
        })
    }

    return mappings
}

/**
 * Finds the best matching source field for a target field name.
 */
function findBestMatch(targetName, sourceFields) {
    const normalizedTarget = targetName.toLowerCase().replace(/[^a-z0-9]/g, '')

    // Exact match
    let match = sourceFields.find(f => f.name.toLowerCase() === targetName.toLowerCase())
    if (match) return match

    // ID mappings: 'restaurant_id' -> 'id'
    if (normalizedTarget.endsWith('id')) {
        const base = normalizedTarget.replace('id', '')
        // Look for 'id' if there's only one 'id' or a prefixed one
        match = sourceFields.find(f => f.name.toLowerCase() === 'id')
        if (match) return match

        match = sourceFields.find(f => f.name.toLowerCase().includes(base) && f.name.toLowerCase().includes('id'))
        if (match) return match
    }

    return null
}
