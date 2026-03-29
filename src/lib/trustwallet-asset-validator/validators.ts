import type { AssetInfo, AssetLink } from './types';
import {
  allowedLinkKeys,
  allowedStatusValues,
  whiteSpaceCharacters,
} from './values';

export function validateLinks(links: AssetLink[]): string | null {
  if (!links || links.length < 2) {
    return null;
  }

  for (const link of links) {
    if (!link.name || !link.url) {
      return 'Missing required fields links.url and links.name';
    }

    if (!(link.name in allowedLinkKeys)) {
      return `Invalid value for links.name field, allowed only: ${Object.keys(allowedLinkKeys).join(', ')}`;
    }

    if (!link.url.startsWith('https://')) {
      return 'Invalid value for links.url field, allowed only with https:// prefix';
    }

    const prefixes = allowedLinkKeys[link.name];
    if (prefixes.length > 0) {
      const hasValidPrefix = prefixes.some((prefix) =>
        link.url?.startsWith(prefix),
      );
      if (!hasValidPrefix) {
        return `Invalid value '${link.url}' for ${link.name} link url, allowed only with prefix: ${prefixes.join(' or ')}`;
      }
    }

    if (link.name === 'medium' && !link.url.includes('medium.com')) {
      return 'Invalid value for links.url field, should contain medium.com';
    }
  }

  return null;
}

export function validateStatus(status: string): string | null {
  if (!allowedStatusValues.includes(status)) {
    return `Invalid status field, allowed values: ${allowedStatusValues.join(', ')}`;
  }
  return null;
}

export function validateDescription(description: string): string | null {
  if (description.length > 600) {
    return 'Invalid length for description field';
  }

  for (const ch of whiteSpaceCharacters) {
    if (description.includes(ch)) {
      return 'Description contains not allowed characters (new line, double space)';
    }
  }

  return null;
}

export function validateAssetInfo(asset: AssetInfo): string[] {
  const errors: string[] = [];

  if (asset.status) {
    const statusErr = validateStatus(asset.status);
    if (statusErr) errors.push(statusErr);
  }

  if (asset.description) {
    const descErr = validateDescription(asset.description);
    if (descErr) errors.push(descErr);
  }

  if (asset.links) {
    const linksErr = validateLinks(asset.links);
    if (linksErr) errors.push(linksErr);
  }

  return errors;
}
