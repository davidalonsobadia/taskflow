export const config = {
  app: {
    name: "TaskFlow",
    description: "Modern TODO list platform",
  },
  api: {
    // Real backend API configuration
    baseUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
    apiKey: process.env.NEXT_PUBLIC_API_KEY || "PI1u-i-6i2pGeIi9q6OOaYYLc7BnjCHzJ58m0NEaIrM",
    endpoints: {
      // Backend API endpoints (v1)
      backend: {
        auth: {
          register: "/api/v1/auth/register",
          login: "/api/v1/auth/login",
          logout: "/api/v1/auth/logout",
          verifyEmail: "/api/v1/auth/verify-email",
          forgotPassword: "/api/v1/auth/forgot-password",
          resetPassword: "/api/v1/auth/reset-password",
          me: "/api/v1/auth/me",
        },
        lists: {
          base: "/api/v1/lists",
          byId: (id: string) => `/api/v1/lists/${id}`,
        },
        tasks: {
          base: "/api/v1/tasks",
          byId: (id: string) => `/api/v1/tasks/${id}`,
        },
      },
      // Frontend API routes (proxy to backend)
      auth: {
        register: "/api/auth/register",
        login: "/api/auth/login",
        logout: "/api/auth/logout",
        verifyEmail: "/api/auth/verify-email",
        forgotPassword: "/api/auth/forgot-password",
        resetPassword: "/api/auth/reset-password",
        me: "/api/auth/me",
      },
      lists: {
        base: "/api/lists",
        byId: (id: string) => `/api/lists/${id}`,
      },
      tasks: {
        base: "/api/tasks",
        byId: (id: string) => `/api/tasks/${id}`,
      },
    },
  },
  routes: {
    home: "/",
    login: "/login",
    register: "/register",
    verifyEmail: "/verify-email",
    forgotPassword: "/forgot-password",
    resetPassword: "/reset-password",
    lists: "/lists",
    listDetail: (id: string) => `/lists/${id}`,
  },
} as const
