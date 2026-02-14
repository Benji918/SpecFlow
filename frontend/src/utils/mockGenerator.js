import { faker } from '@faker-js/faker'

/**
 * Generates mock data based on a JSON schema
 * @param {Object} schema - JSON schema object
 * @returns {any} Mock data
 */
export function generateMockFromSchema(schema) {
    if (!schema) return null

    // Handle references
    if (schema.$ref) {
        return { message: 'Reference not supported in simplified generator' }
    }

    // NEW: Handle top-level enum immediately regardless of type
    if (schema.enum && Array.isArray(schema.enum)) {
        return faker.helpers.arrayElement(schema.enum)
    }

    // NEW: Handle composition patterns (allOf, anyOf, oneOf)
    // Common in OpenAPI when combining a base type with an enum or extra validation
    if (schema.allOf && Array.isArray(schema.allOf)) {
        // Find a sub-schema that has the actual type or enum
        for (const sub of schema.allOf) {
            const mock = generateMockFromSchema(sub)
            if (mock !== null) return mock
        }
    }

    if ((schema.anyOf || schema.oneOf) && Array.isArray(schema.anyOf || schema.oneOf)) {
        const options = schema.anyOf || schema.oneOf
        return generateMockFromSchema(faker.helpers.arrayElement(options))
    }

    const type = schema.type || (schema.properties ? 'object' : 'string')

    switch (type) {
        case 'string':
            if (schema.format === 'binary') {
                // If it's binary, it's likely a file upload.
                // Return a placeholder image URL that the executor can fetch.
                const name = (schema.title || schema.name || '').toLowerCase()
                if (name.includes('image') || name.includes('photo') || name.includes('avatar') || schema.pattern?.includes('jpg|jpeg|png')) {
                    // Use a specific high-quality image placeholder with a random seed for fresh data
                    const sig = Math.floor(Math.random() * 1000)
                    return `https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=500&h=500&fit=crop&sig=${sig}`
                }
                return 'https://via.placeholder.com/500'
            }
            if (schema.format === 'date-time') return faker.date.recent().toISOString()
            if (schema.format === 'date') return faker.date.recent().toISOString().split('T')[0]
            if (schema.format === 'email') return faker.internet.email()
            if (schema.format === 'uuid') return faker.string.uuid()

            // Try to guess by name
            const name = schema.title || schema.name || ''
            if (name.toLowerCase().includes('name')) return faker.person.fullName()
            if (name.toLowerCase().includes('company')) return faker.company.name()
            if (name.toLowerCase().includes('phone')) return faker.phone.number()
            if (name.toLowerCase().includes('address')) return faker.location.streetAddress()
            if (name.toLowerCase().includes('id')) return faker.string.uuid()

            return faker.lorem.words(3)

        case 'number':
        case 'integer':
            const min = schema.minimum || 0
            const max = schema.maximum || 1000
            return type === 'integer' ? faker.number.int({ min, max }) : faker.number.float({ min, max })

        case 'boolean':
            return faker.datatype.boolean()

        case 'array':
            const minItems = schema.minItems || 1
            const maxItems = schema.maxItems || 3
            const count = faker.number.int({ min: minItems, max: maxItems })
            const items = []
            for (let i = 0; i < count; i++) {
                items.push(generateMockFromSchema(schema.items))
            }
            return items

        case 'object':
            const obj = {}
            if (schema.properties) {
                for (const [key, prop] of Object.entries(schema.properties)) {
                    // Pass key as Hint
                    const subSchema = { ...prop, name: key }
                    obj[key] = generateMockFromSchema(subSchema)
                }
            }
            return obj

        default:
            return null
    }
}

/**
 * Generates mock data for an endpoint based on its parameters and requestBody
 * @param {Object} endpoint - Endpoint definition
 * @returns {Object} Mock data including body and params
 */
export function generateEndpointMock(endpoint) {
    // Ensure fresh entropy for each call to avoid repeating data on sequential clicks
    faker.seed(Math.floor(Math.random() * 1000000))

    const mock = {
        body: null,
        params: {}
    }

    // 1. Identify valid spec (don't use binary data/existing body as spec)
    let spec = endpoint.requestBodySpec
    if (!spec && endpoint.requestBody && typeof endpoint.requestBody === 'object' && endpoint.requestBody.content) {
        spec = endpoint.requestBody
    }

    const content = spec?.content
    if (content) {
        // Try to find a schema in common content types
        const types = ['application/json', 'multipart/form-data', 'application/x-www-form-urlencoded']
        for (const type of types) {
            if (content[type]?.schema) {
                mock.body = generateMockFromSchema(content[type].schema)
                break
            }
        }
    }

    if (endpoint.parameters) {
        endpoint.parameters.forEach(param => {
            if (param.schema) {
                mock.params[param.name] = generateMockFromSchema(param.schema)
            }
        })
    }

    return mock
}
