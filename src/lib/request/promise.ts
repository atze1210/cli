import { EXIT_CODES } from '../../cli/exit-codes';
import { getAuthHeader } from '../api-token';
import { MissingApiTokenError } from '../errors';
import { headerSnykAuthFailed, headerSnykTsCliTerminate } from './constants';
import * as request from './index';

export async function makeRequest<T>(payload: any): Promise<T> {
  return new Promise((resolve, reject) => {
    request.makeRequest(payload, (error, res, body) => {
      if (res?.headers?.[headerSnykTsCliTerminate] == 'true') {
        process.exit(EXIT_CODES.EX_TERMINATE);
      }

      if (error) {
        return reject(error);
      }
      if (res.statusCode !== 200) {
        return reject({
          code: res.statusCode,
          message: body?.message,
        });
      }
      resolve(body);
    });
  });
}

/**
 * All rest request will essentially be the same and are JSON by default
 * Thus if no headers provided default headers are used
 * @param {any} payload for the request
 * @returns
 */
export async function makeRequestRest<T>(payload: any): Promise<T> {
  return new Promise((resolve, reject) => {
    payload.headers = payload.headers ?? {
      'Content-Type': 'application/vnd.api+json',
      authorization: getAuthHeader(),
    };
    payload.json = true;
    payload.parse = false; // do not use needle auto parser, using JSON.parse below
    request.makeRequest(payload, (error, res, body) => {
      if (error) {
        return reject(error);
      }
      if (res?.headers?.[headerSnykAuthFailed] === 'true') {
        return reject(new MissingApiTokenError());
      }
      if (res.statusCode >= 400) {
        const parsedBody = parseJsonBody(body);

        return reject({
          code: res.statusCode,
          ...(parsedBody && typeof parsedBody === 'object'
            ? { body: parsedBody, message: (parsedBody as any).message }
            : {}),
        });
      }
      resolve(JSON.parse(body as any) as T);
    });
  });
}

function parseJsonBody(body: any): unknown {
  if (typeof body !== 'string') {
    return body;
  }

  try {
    return JSON.parse(body);
  } catch {
    return undefined;
  }
}
