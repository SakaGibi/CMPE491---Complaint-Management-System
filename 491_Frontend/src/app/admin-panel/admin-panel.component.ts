import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';



@Component({
  selector: 'app-admin-panel',
  imports: [FormsModule, CommonModule],
  templateUrl: './admin-panel.component.html',
  styleUrl: './admin-panel.component.css'
})
export class AdminPanelComponent {

  username: string = '';
  password: string = '';
  email: string = '';
  role: 'employee' | 'admin' = 'employee';
  isAdmin: boolean = false;
  addUserMessage: string = '';
  userList: any[] = [];
  selectedUser: any = null;
  isUserModalOpen: boolean = false;

  constructor(
    private router: Router,
    private apiService: ApiService
  ){}

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }

  openUserModal(user: any): void {
    this.selectedUser = user;
    this.isUserModalOpen = true;
  }
  
  closeUserModal(): void {
    this.isUserModalOpen = false;
    this.selectedUser = null;
  }

  addNewUser(): void {
    this.addUserMessage = '';
  
    const username = this.username.trim();
    const password = this.password.trim();
    const email = this.email.trim();
  
    if (!username || !password || !email) {
      this.addUserMessage = 'Kullanıcı adı, şifre ve e‑posta zorunludur.';
      return;
    }
  
    if (this.role !== 'employee' && this.role !== 'admin') {
      this.addUserMessage = 'Geçersiz rol.';
      return;
    }
  
    const payload = {
      username,
      password,
      email,
      role: this.role as 'employee' | 'admin'
    };
  
    console.log('[addUser] Payload:', payload);
  
    this.apiService.addUser(payload).subscribe({
      next: (res) => {
        console.log('[addUser] Başarılı:', res);
        this.addUserMessage = 'Kullanıcı başarıyla eklendi.';
        this.username = '';
        this.password = '';
        this.email = '';
        this.role = 'employee';
        this.isAdmin = false;
      },
      error: (err) => {
        console.error('[addUser] Hata:', err);
        this.addUserMessage = err.error?.error || 'Bir hata oluştu.';
      }
    });
  }

  loadUsers(): void {
    this.apiService.getUserList().subscribe({
      next: (res) => {
        console.log('[User List]', res);
        this.userList = res;
      },
      error: (err) => {
        console.error('[User List HATA]', err);
      }
    });
  }

  ngOnInit(): void {
    this.loadUsers();
  }
  

}
