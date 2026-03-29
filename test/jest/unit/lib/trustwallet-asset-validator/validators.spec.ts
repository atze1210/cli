import {
  validateLinks,
  validateStatus,
  validateDescription,
  validateAssetInfo,
  allowedLinkKeys,
} from '../../../../../src/lib/trustwallet-asset-validator';

describe('trustwallet-asset-validator', () => {
  describe('allowedLinkKeys', () => {
    it('should include "twitter" as a valid link key', () => {
      expect(Object.keys(allowedLinkKeys).includes('twitter')).toBe(true);
    });

    it('should not include "x" as a valid link key', () => {
      expect(Object.keys(allowedLinkKeys).includes('x')).toBe(false);
    });

    it('should include "github" as a valid link key', () => {
      expect(Object.keys(allowedLinkKeys).includes('github')).toBe(true);
    });
  });

  describe('validateLinks', () => {
    it('should return null for fewer than 2 links', () => {
      expect(
        validateLinks([{ name: 'twitter', url: 'https://x.com/test' }]),
      ).toBeNull();
      expect(validateLinks([])).toBeNull();
    });

    it('should accept "twitter" link with https://x.com/ prefix', () => {
      const links = [
        { name: 'twitter', url: 'https://x.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      expect(validateLinks(links)).toBeNull();
    });

    it('should accept "twitter" link with https://twitter.com/ prefix', () => {
      const links = [
        { name: 'twitter', url: 'https://twitter.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      expect(validateLinks(links)).toBeNull();
    });

    it('should accept "github" link with https://github.com/ prefix', () => {
      const links = [
        {
          name: 'github',
          url: 'https://github.com/ExpertVagabond/purp-contracts',
        },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      expect(validateLinks(links)).toBeNull();
    });

    it('should reject "x" as a link name', () => {
      const links = [
        { name: 'x', url: 'https://x.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      const result = validateLinks(links);
      expect(result).not.toBeNull();
      expect(result).toContain('Invalid value for links.name field');
    });

    it('should reject links without name', () => {
      const links = [
        { url: 'https://x.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      const result = validateLinks(links);
      expect(result).not.toBeNull();
      expect(result).toContain('Missing required fields');
    });

    it('should reject links without https:// prefix', () => {
      const links = [
        { name: 'twitter', url: 'http://x.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      const result = validateLinks(links);
      expect(result).not.toBeNull();
      expect(result).toContain('https://');
    });

    it('should reject twitter link with wrong URL prefix', () => {
      const links = [
        { name: 'twitter', url: 'https://wrongsite.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
      ];
      const result = validateLinks(links);
      expect(result).not.toBeNull();
      expect(result).toContain('twitter');
    });

    it('should reject medium link without medium.com in URL', () => {
      const links = [
        { name: 'medium', url: 'https://example.com/article' },
        { name: 'telegram', url: 'https://t.me/test' },
      ];
      const result = validateLinks(links);
      expect(result).not.toBeNull();
      expect(result).toContain('medium.com');
    });

    it('should accept valid info.json links from the referenced commit', () => {
      const links = [
        { name: 'twitter', url: 'https://x.com/squirrel_eth' },
        { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
        {
          name: 'github',
          url: 'https://github.com/ExpertVagabond/purp-contracts',
        },
      ];
      expect(validateLinks(links)).toBeNull();
    });
  });

  describe('validateStatus', () => {
    it('should accept "active" status', () => {
      expect(validateStatus('active')).toBeNull();
    });

    it('should accept "spam" status', () => {
      expect(validateStatus('spam')).toBeNull();
    });

    it('should accept "abandoned" status', () => {
      expect(validateStatus('abandoned')).toBeNull();
    });

    it('should reject unknown status values', () => {
      const result = validateStatus('invalid');
      expect(result).not.toBeNull();
      expect(result).toContain('Invalid status field');
    });
  });

  describe('validateDescription', () => {
    it('should accept a valid description', () => {
      expect(
        validateDescription('Native utility token for Purple Squirrel Media.'),
      ).toBeNull();
    });

    it('should reject descriptions longer than 600 characters', () => {
      const longDesc = 'a'.repeat(601);
      const result = validateDescription(longDesc);
      expect(result).not.toBeNull();
      expect(result).toContain('length');
    });

    it('should reject descriptions with newlines', () => {
      const result = validateDescription('Line one\nLine two');
      expect(result).not.toBeNull();
      expect(result).toContain('new line');
    });

    it('should reject descriptions with double spaces', () => {
      const result = validateDescription('Hello  World');
      expect(result).not.toBeNull();
    });
  });

  describe('validateAssetInfo', () => {
    it('should return no errors for a valid asset info matching the referenced commit', () => {
      const asset = {
        name: 'Purple Squirrel',
        website: 'https://purplesquirrel.media',
        description:
          'Native utility token for Purple Squirrel Media DePIN satellite ground station network.',
        explorer:
          'https://etherscan.io/token/0x1A3efe6077114fba442BcDa3DD6A3500171A4Dc6',
        type: 'ERC20',
        symbol: 'PURP',
        decimals: 9,
        status: 'active',
        id: '0x1A3efe6077114fba442BcDa3DD6A3500171A4Dc6',
        tags: ['defi'],
        links: [
          { name: 'twitter', url: 'https://x.com/squirrel_eth' },
          { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
          {
            name: 'github',
            url: 'https://github.com/ExpertVagabond/purp-contracts',
          },
        ],
      };
      expect(validateAssetInfo(asset)).toEqual([]);
    });

    it('should report errors for asset info with "x" link name', () => {
      const asset = {
        status: 'active',
        description: 'A token.',
        links: [
          { name: 'x', url: 'https://x.com/squirrel_eth' },
          { name: 'telegram', url: 'https://t.me/purplesquirrelmedia' },
        ],
      };
      const errors = validateAssetInfo(asset);
      expect(errors.length).toBeGreaterThan(0);
      expect(errors[0]).toContain('Invalid value for links.name field');
    });
  });
});
