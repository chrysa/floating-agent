import React from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import "./styles/global.scss";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchInterval: 5000, staleTime: 4000 },
  },
});

const container = document.getElementById("root");
if (!container) throw new Error("No #root element");

createRoot(container).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
