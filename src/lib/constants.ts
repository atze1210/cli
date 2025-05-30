// Separator used while displaying various paths (e.g. package paths, call
// paths) to the user
export const PATH_SEPARATOR = ' > ';

// String used to signify hidden path elements e.g. for abbreviated paths
export const PATH_HIDDEN_ELEMENTS = '...';

// Number of function names to show in the beginning of an abbreviated call path
export const CALL_PATH_LEADING_ELEMENTS = 2;

// Number of function names to show in the end of an abbreviated call path
export const CALL_PATH_TRAILING_ELEMENTS = 2;

// Upper limit of string length that should be allowed for output to stdrr || stdout.
// Use when outputting strings of unknown length. e.g. response payloads
export const MAX_STRING_LENGTH = 50000;
