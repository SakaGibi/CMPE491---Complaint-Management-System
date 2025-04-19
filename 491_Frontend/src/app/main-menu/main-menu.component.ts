import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-main-menu',
  imports: [FormsModule, CommonModule],
  templateUrl: './main-menu.component.html',
  styleUrl: './main-menu.component.css',
  host: { 'ngSkipHydration': 'true' }
})
export class MainMenuComponent {

  complaintNumber: string = '';
  complaintStatus: string = '';
  isTracking: boolean = false;
  complaintText: string = '';
  email: string = '';

  constructor(
    private router: Router,
    private apiService: ApiService
  ){}

  writeComplaintOrSuggestion() {
    console.log('Fonksiyon tetiklendi');

    if (!this.complaintText || this.complaintText.trim() === '') {
      alert('Lütfen şikayet ya da öneri metni girin.');
      return;
    }
  
    if (this.isTracking && (!this.email || this.email.trim() === '')) {
      alert('Takip etmek için e‑posta adresi gereklidir.');
      return;
    }
  
    const payload = {
      description: this.complaintText,
      isTrackable: this.isTracking,
      email: this.isTracking ? this.email : undefined,
    };
  
    console.log('Payload:', payload);
  
    this.apiService.submitComplaintOrSuggestion(payload).subscribe({
      next: (res) => {
        console.log('BAŞARILI:', res);
        alert('Şikayet/Bilgi başarıyla gönderildi.');
        this.closeModal();
        this.resetModal();
      },
      error: (err) => {
        console.error('HATA:', err);
        alert('Bir hata oluştu: ' + (err.error?.error || 'Sunucuya ulaşılamadı.'));
      },
    });
  }

  toggleEmailInput() {
    const checkbox = document.getElementById('trackCheckBox') as HTMLInputElement | null;
    const emailInput = document.getElementById('emailInputContainer') as HTMLElement | null;

    if (checkbox && emailInput) { 
      if (checkbox.checked) {
        emailInput.style.display = 'block'; 
      } else {
        emailInput.style.display = 'none'; 
      }
    }
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToManagementPanelLogin() {
    this.router.navigate(['/managementPanelLogin']);
  }

  openModal() {
    const modal = document.getElementById('complaintModal');
    if (modal) {
      modal.style.display = 'flex';
    }
  }
  
  closeModal() {
    const modal = document.getElementById('complaintModal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  trackComplaint(event: Event) {
    event.preventDefault();
    if (this.complaintNumber.trim() !== '') {
      this.complaintStatus = `Complaint #${this.complaintNumber} is currently being processed.`; // Dinamik veri buraya bağlanabilir
      this.isTracking = true;
    } else {
      this.complaintStatus = 'Please enter a valid complaint number.';
    }
  }

  resetModal() {
    this.complaintNumber = '';
    this.complaintStatus = '';
    this.isTracking = false;
  }
  

}
