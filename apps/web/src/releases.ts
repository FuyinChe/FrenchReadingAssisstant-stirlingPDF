export const GITHUB_REPO = "FuyinChe/FrenchReadingAssisstant-stirlingPDF";
export const RELEASES_LATEST_PAGE = `https://github.com/${GITHUB_REPO}/releases/latest`;
export const RELEASES_API = `https://api.github.com/repos/${GITHUB_REPO}/releases/latest`;

export type PlatformId = "windows-x64" | "macos-arm64" | "macos-x64";

type GithubAsset = {
  name: string;
  browser_download_url: string;
};

type GithubRelease = {
  tag_name: string;
  html_url: string;
  assets: GithubAsset[];
};

export type ReleaseInfo = {
  tag: string;
  htmlUrl: string;
  urls: Partial<Record<PlatformId, string>>;
};

function matchPlatform(name: string): PlatformId | null {
  const lower = name.toLowerCase();
  if (!lower.endsWith(".zip")) {
    return null;
  }
  if (lower.includes("windows")) {
    return "windows-x64";
  }
  if (lower.includes("macos-arm64") || lower.includes("darwin-arm")) {
    return "macos-arm64";
  }
  if (lower.includes("macos-x64") || lower.includes("darwin-x64")) {
    return "macos-x64";
  }
  return null;
}

export async function fetchLatestRelease(): Promise<ReleaseInfo | null> {
  const response = await fetch(RELEASES_API, {
    headers: { Accept: "application/vnd.github+json" },
  });
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error(`GitHub API ${response.status}`);
  }
  const body = (await response.json()) as GithubRelease;
  const urls: Partial<Record<PlatformId, string>> = {};
  for (const asset of body.assets ?? []) {
    const platform = matchPlatform(asset.name);
    if (platform) {
      urls[platform] = asset.browser_download_url;
    }
  }
  return {
    tag: body.tag_name,
    htmlUrl: body.html_url || RELEASES_LATEST_PAGE,
    urls,
  };
}
