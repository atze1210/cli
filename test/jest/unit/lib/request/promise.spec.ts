import * as request from '../../../../../src/lib/request';
import { makeRequestRest } from '../../../../../src/lib/request/promise';

describe('makeRequestRest', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('preserves parsed JSON API error bodies for non-400 responses', async () => {
    jest.spyOn(request, 'makeRequest').mockImplementation(
      async (_payload, callback) => {
        callback?.(
          null,
          {
            statusCode: 404,
            headers: {},
          },
          JSON.stringify({
            jsonapi: {
              version: '1.0',
            },
            errors: [
              {
                status: '404',
                detail: 'App not found',
              },
            ],
          }),
        );
      },
    );

    await expect(makeRequestRest({ headers: {} })).rejects.toMatchObject({
      code: 404,
      body: {
        errors: [
          {
            detail: 'App not found',
            status: '404',
          },
        ],
      },
    });
  });
});
