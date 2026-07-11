import {supabase} from './supabase';
const API_BASE=import.meta.env.VITE_API_BASE_URL as string;
export async function api<T>(path:string,init:RequestInit={}){const {data}=await supabase.auth.getSession();const headers=new Headers(init.headers);headers.set('Content-Type','application/json');if(data.session?.access_token)headers.set('Authorization',`Bearer ${data.session.access_token}`);const res=await fetch(`${API_BASE}${path}`,{...init,headers});if(!res.ok)throw new Error((await res.text())||'요청 실패');return res.json() as Promise<T>}
