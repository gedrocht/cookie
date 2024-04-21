const request = require('supertest');
const app = require('./app');

describe('POST /reverse', () => {
    it('should reverse a string', async () => {
        const response = await request(app)
          .post('/reverse')
          .send({ text: 'hello' })
          .expect(200);
        expect(response.body.reversed).toEqual('olleh');
    });
});
