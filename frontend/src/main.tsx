import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import './styles/index.css';
import { PublicLayout } from './layouts/PublicLayout';
import { AdminLayout } from './layouts/AdminLayout';
import { HomePage } from './pages/HomePage';
import { ArticlePage } from './pages/ArticlePage';
import { LoginPage } from './pages/LoginPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { AdminDevicesPage } from './pages/AdminDevicesPage';
import { AdminSchedulesPage } from './pages/AdminSchedulesPage';
import { AdminLogsPage } from './pages/AdminLogsPage';
import { AdminContentPage } from './pages/AdminContentPage';
import { AdminPlantsPage } from './pages/AdminPlantsPage';
import { AdminThemesPage } from './pages/AdminThemesPage';
import { RequireAdmin } from './components/RequireAdmin';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/article/:slug" element={<ArticlePage />} />
          <Route path="/plant/:slug" element={<ArticlePage />} />
        </Route>

        <Route path="/admin/login" element={<LoginPage />} />
        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminLayout />
            </RequireAdmin>
          }
        >
          <Route index element={<AdminDashboardPage />} />
          <Route path="content" element={<AdminContentPage />} />
          <Route path="plants" element={<AdminPlantsPage />} />
          <Route path="themes" element={<AdminThemesPage />} />
          <Route path="devices" element={<AdminDevicesPage />} />
          <Route path="schedules" element={<AdminSchedulesPage />} />
          <Route path="logs" element={<AdminLogsPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
);
