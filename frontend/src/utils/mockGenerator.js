import { faker } from '@faker-js/faker'

/**
 * Generates mock data based on a JSON schema
 * @param {Object} schema - JSON schema object
 * @returns {any} Mock data
 */
export function generateMockFromSchema(schema) {
    if (!schema) return null

    // Handle references (simplified, assuming they are resolved or not used for now)
    if (schema.$ref) {
        return { message: 'Reference not supported in simplified generator' }
    }

    const type = schema.type || (schema.properties ? 'object' : 'string')

    switch (type) {
        case 'string':
            if (schema.format === 'date-time') return faker.date.recent().toISOString()
            if (schema.format === 'date') return faker.date.recent().toISOString().split('T')[0]
            if (schema.format === 'email') return faker.internet.email()
            if (schema.format === 'uuid') return faker.string.uuid()
            if (schema.enum) return faker.helpers.arrayElement(schema.enum)

            // Try to guess by name
            const name = schema.title || schema.name || ''
            if (name.toLowerCase().includes('name')) return faker.person.fullName()
            if (name.toLowerCase().includes('company')) return faker.company.name()
            if (name.toLowerCase().includes('phone')) return faker.phone.number()
            if (name.toLowerCase().includes('address')) return faker.location.streetAddress()

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
                    prop.name = key
                    obj[key] = generateMockFromSchema(prop)
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
    const mock = {
        body: null,
        params: {}
    }

    if (endpoint.requestBody?.content?.['application/json']?.schema) {
        mock.body = generateMockFromSchema(endpoint.requestBody.content['application/json'].schema)
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
