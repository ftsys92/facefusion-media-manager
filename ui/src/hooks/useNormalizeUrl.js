export const useNormalizeUrl = (url) => {
    url = url.trim().replace(/\/+$/, "");
    if (!/^https?:\/\//i.test(url)) {
        url = 'https://' + url;
    }
    url = url.replace(/^http:\/\//i, 'https://');
    return url;
}