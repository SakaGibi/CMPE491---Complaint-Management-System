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
}