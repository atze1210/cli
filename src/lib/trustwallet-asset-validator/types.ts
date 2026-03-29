export interface AssetLink {
  name?: string;
  url?: string;
}

export interface AssetInfo {
  name?: string;
  symbol?: string;
  type?: string;
  decimals?: number;
  description?: string;
  website?: string;
  explorer?: string;
  research?: string;
  status?: string;
  id?: string;
  tags?: string[];
  links?: AssetLink[];
}
