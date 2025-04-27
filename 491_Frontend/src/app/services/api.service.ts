import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private BASE_URL = 'http://127.0.0.1:8000/api';

  constructor(private http: HttpClient) {}

  submitComplaintOrSuggestion(data: {
    description: string;
    isTrackable: boolean;
    email?: string;
  }): Observable<any> {
    return this.http.post(`${this.BASE_URL}/complaints/submit/`, data);
  }

  trackComplaint(id: number): Observable<any> {
    return this.http.get(`${this.BASE_URL}/complaints/track/${id}/`);
  }

  employeeLogin(credentials: {username: string; password: string }): Observable<any> {
    return this.http.post(`${this.BASE_URL}/employees/login/`, credentials);
  }

  getFAQs(): Observable<any[]> {
    return this.http.get<any[]>(`${this.BASE_URL}/support/faq/`);
  }
  
  submitSupportMessage(data: { email: string; message: string }): Observable<any> {
    return this.http.post(`${this.BASE_URL}/support/submit/`, {
      email: data.email,
      message: data.message
    });
  }

  addUser(data: {
    username: string;
    password: string;
    email?: string;
    role: 'employee' | 'admin';
  }): Observable<any> {
    return this.http.post(`${this.BASE_URL}/employees/add/`, data);
  }

  getUserList(): Observable<any[]> {
    return this.http.get<any[]>(`${this.BASE_URL}/employees/list/`);
  }

  deleteUser(payload: { username: string }): Observable<any> {
    return this.http.request('delete', `${this.BASE_URL}/employees/delete/`, { body: payload });
  }
  
  changeUserRole(payload: { username: string, role: 'admin' | 'employee' }): Observable<any> {
    return this.http.put(`${this.BASE_URL}/employees/change-role/`, payload);
  }
  
  getSupportMessages(): Observable<any[]> {
    return this.http.get<any[]>(`${this.BASE_URL}/support/list/`);
  }
  
  deleteSupportMessage(messageId: number): Observable<any> {
    return this.http.delete(`${this.BASE_URL}/support/delete/${messageId}/`);
  }

  getComplaints(params?: any): Observable<any[]> {
    console.log('[API] getComplaints çağrıldı, params:', params);
    return this.http.get<any[]>(`${this.BASE_URL}/complaints/complaints/`, { params });
  }
  
  getComplaintById(complaintId: number): Observable<any> {
    console.log(`[API] getComplaintById çağrıldı. ID: ${complaintId}`);
    return this.http.get<any>(`${this.BASE_URL}/complaints/detail/${complaintId}/`);
  }

  updateComplaintStatus(complaintId: number, status: string): Observable<any> {
    console.log('[API] Durum güncelleme başlatıldı:', { complaintId, status });
    return this.http.put(`${this.BASE_URL}/complaints/update-status/${complaintId}/`, { status });
  }
  
  deleteComplaint(complaintId: number): Observable<any> {
    console.log('[API] Şikayet silme başlatıldı:', complaintId);
    return this.http.delete(`${this.BASE_URL}/complaints/delete/${complaintId}/`);
  }

  getSuggestions(): Observable<any[]> {
    const params = { type: 'suggestion' };
    console.log('[API] getSuggestions çağrıldı, params:', params);
    return this.http.get<any[]>(`${this.BASE_URL}/complaints/complaints/`, { params });
  }

  getComplaintStatistics(range?: string): Observable<any[]> {
    const params: any = {};
    if (range) params.range = range;
    return this.http.get<any[]>(`${this.BASE_URL}/complaints/statistics/`, { params });
  }

  getComplaintTrends(params?: any): Observable<any[]> {
    return this.http.get<any[]>(`${this.BASE_URL}/complaints/trends/`, { params });
  }
}