import {Navigate,Outlet,useLocation} from 'react-router-dom';import {useAuth} from '@/features/auth/AuthContext';
export function ProtectedRoute(){const{session,loading}=useAuth();const loc=useLocation();if(loading)return <main className="p-6">세션을 확인하고 있습니다...</main>;return session?<Outlet/>:<Navigate to="/login" replace state={{from:loc.pathname}}/>}
