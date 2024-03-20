import axios from "axios"

import axios from axios;

const getAuthToken = () => localStorage.getItem('ff_token');

const httpClient = axios.create({
    baseURL: process.env.VITE_FACEFUSION_BASE_URL,
    headers: {
        "Content-Type": "application/json",
        // anything you want to add to the headers
    }
});

const authInterceptor = (config) => {
    const token = getAuthToken();

    if (token) {
        config.headers['Authorization'] = `Bearer ${getAuthToken()}`;
    }

    return config;
}

httpClient.interceptors.request.use(authInterceptor);

export default httpClient;