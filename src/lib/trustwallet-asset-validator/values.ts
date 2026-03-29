/**
 * Allowed social/external link keys for TrustWallet asset info.json files.
 * Each key maps to an optional required URL prefix (empty string means no
 * prefix is enforced beyond the mandatory https:// scheme).
 *
 * Note: The canonical key for X / Twitter is "twitter". URLs may use either
 * https://twitter.com/ or https://x.com/ as the domain.
 */
export const allowedLinkKeys: Record<string, string[]> = {
  github: ['https://github.com/'],
  whitepaper: [],
  twitter: ['https://twitter.com/', 'https://x.com/'],
  telegram: ['https://t.me/'],
  telegram_news: ['https://t.me/'],
  medium: [],
  // medium links require "medium.com" to appear in the URL (validated separately)
  discord: ['https://discord.com/'],
  reddit: ['https://reddit.com/'],
  facebook: ['https://facebook.com/'],
  youtube: ['https://youtube.com/'],
  coinmarketcap: ['https://coinmarketcap.com/'],
  coingecko: ['https://coingecko.com/'],
  blog: [],
  forum: [],
  docs: [],
  source_code: [],
};

export const allowedStatusValues: string[] = ['active', 'spam', 'abandoned'];

export const requiredAssetFields: string[] = [
  'name',
  'type',
  'symbol',
  'decimals',
  'description',
  'website',
  'explorer',
  'status',
  'id',
];

export const whiteSpaceCharacters: string[] = ['\n', '  '];
