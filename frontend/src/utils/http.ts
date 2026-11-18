import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from "axios";

export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

const http: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// 请求拦截器
http.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器：用类型断言绕过「返回类型不匹配」的报错
http.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data;

    if (res.code !== 0 && res.code !== 200) {
      if (res.code === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
      return Promise.reject(new Error(res.message || "请求失败"));
    }

    // 关键：把返回类型断言为 any，以匹配 Axios 拦截器的类型签名
    return res.data as any;
  },
  (error) => {
    let message = "网络异常，请稍后重试";
    if (error.response) {
      const status = error.response.status;
      const map: Record<number, string> = {
        400: "请求参数错误",
        401: "登录已过期，请重新登录",
        403: "没有权限访问",
        404: "请求的资源不存在",
        500: "服务器内部错误",
      };
      message = map[status] || `请求失败（${status}）`;
      if (status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    } else if (error.code === "ECONNABORTED") {
      message = "请求超时，请检查网络";
    }
    return Promise.reject(new Error(message));
  },
);

// 对外暴露的请求方法
export const request = {
  // 关键改动：第二个参数直接接收 params 对象
  get<T = unknown>(url: string, params?: Record<string, unknown>): Promise<T> {
    return http.get(url, { params }) as unknown as Promise<T>;
  },

  post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> {
    return http.post(url, data, config) as unknown as Promise<T>;
  },

  put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ): Promise<T> {
    return http.put(url, data, config) as unknown as Promise<T>;
  },

  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return http.delete(url, config) as unknown as Promise<T>;
  },
};

export default http;
