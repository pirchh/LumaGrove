import { Navigate, useLocation } from 'react-router-dom';
import { getToken } from '../api/auth';

type Props = {
  children: React.ReactNode;
};

export function RequireAdmin({ children }: Props) {
  const location = useLocation();
  if (!getToken()) {
    return <Navigate to="/admin/login" replace state={{ from: location }} />;
  }
  return <>{children}</>;
}
