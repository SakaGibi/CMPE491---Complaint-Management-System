import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common'; 
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-management-panel-login',
  imports: [FormsModule, CommonModule],
  templateUrl: './management-panel-login.component.html',
  styleUrl: './management-panel-login.component.css'
})
export class ManagementPanelLoginComponent {

  username: string = '';
  password: string = '';
  loginError: string = '';
  isAdmin: boolean = false;

  constructor(
    private router: Router,
    private apiService: ApiService
  ){}

  loginEmployee(): void {
    console.log('[loginEmployee] Fonksiyon çalıştı.');
  
    this.loginError = '';
  
    const payload = {
      username: this.username?.trim(),
      password: this.password?.trim()
    };
  
    console.log('[loginEmployee] Payload:', payload);
  
    if (!payload.username || !payload.password) {
      this.loginError = 'Kullanıcı adı ve şifre zorunludur.';
      console.warn('[loginEmployee] Eksik alan var:', this.loginError);
      return;
    }
  
    this.apiService.employeeLogin(payload).subscribe({
      next: (res) => {
        console.log('[loginEmployee] Giriş başarılı:', res);
  
        localStorage.setItem('employee_id', res.employee_id);
        localStorage.setItem('role', res.role);
  
        if (this.isAdmin) {
          if (res.role === 'admin') {
            console.log('[loginEmployee] Admin olarak yönlendiriliyor...');
            this.router.navigate(['/adminPanel']);
          } else {
            this.loginError = 'Bu kullanıcı admin değildir.';
            console.warn('[loginEmployee] Admin değil!');
          }
        } else {
          console.log('[loginEmployee] Normal yönetici yönlendiriliyor...');
          this.router.navigate(['/managementPanel']);
        }
      },
      error: (err) => {
        this.loginError = err.error?.error || 'Bir hata oluştu.';
        console.error('[loginEmployee] Giriş hatası:', err);
      }
    });
  }
  
  

  goToManagementPanel() {
    this.router.navigate(['/managementPanel']);
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }

  changeIsAdmin(){
    this.isAdmin = !this.isAdmin
  }
  
  onLoginSubmit() {
    if (this.isAdmin) {
      this.router.navigate(['/adminPanel']);
    } else {
      this.router.navigate(['/managementPanel']);
    }
  }

}
