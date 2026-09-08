import { handleRestError } from '../../../../../src/lib/apps/rest-utils';

describe('apps rest utils', () => {
  it('surfaces structured API error details', () => {
    expect(() =>
      handleRestError({
        code: 400,
        body: {
          jsonapi: {
            version: '1.0',
          },
          errors: [
            {
              status: '400',
              detail: 'Name has already been taken',
              source: {
                pointer: '/data/attributes/name',
              },
              meta: {
                trace: 'abc123',
              },
            },
          ],
        },
      }),
    ).toThrow(`Uh oh! an error occurred while trying to create the Snyk App.

Error Description:\tName has already been taken
Request Status:\t400
Source:\tpointer: /data/attributes/name

Meta:\ttrace: abc123
`);
  });

  it('falls back to the generic message when the API does not return errors', () => {
    expect(() =>
      handleRestError({
        code: 404,
        body: {
          jsonapi: {
            version: '1.0',
          },
        },
      }),
    ).toThrow(`Uh oh! an error occurred while trying to create the Snyk App.
Please run the command with '--debug' or '-d' to get more information`);
  });
});
