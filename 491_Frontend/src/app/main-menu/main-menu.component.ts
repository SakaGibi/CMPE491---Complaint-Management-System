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
  complaintStatus: any = null;
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

  trackComplaint(event: Event): void {
    event.preventDefault();
  
    const trimmedId = this.complaintNumber.trim();
    const id = Number(trimmedId);
  
    if (!trimmedId || isNaN(id)) {
      this.complaintStatus = { error: 'Please enter a valid complaint number.' };
      this.isTracking = true;
      return;
    }
  
    this.apiService.trackComplaint(id).subscribe({
      next: (res) => {
        console.log('TRACK RESPONSE:', res);
  
        this.complaintStatus = {
          status: res.status,
          category: `${res.category} > ${res.sub_category}`,
          description: res.description,
          created_at: res.created_at,
          updated_at: res.updated_at,
          trackable: res.isTrackable ? 'Yes' : 'No'
        };
  
        this.isTracking = true;
      },
      error: (err) => {
        console.error('Şikayet takibi hatası:', err);
  
        this.complaintStatus = {
          error: err.status === 404 ? 'Complaint not found.' : 'Something went wrong. Please try again.'
        };
  
        this.isTracking = true;
      }
    });
  }
  

  resetModal(): void {
    this.complaintText = '';
    this.email = '';
    this.complaintNumber = '';
    this.complaintStatus = '';
    this.isTracking = false;
  }
  
  convertToISOFormat(dateStr: string | undefined | null): string | null {
    if (!dateStr || typeof dateStr !== 'string') return null;

    const parts = dateStr.split(' ');
    if (parts.length !== 2) return null;

    const [datePart, timePart] = parts;
    const [day, month, year] = datePart.split('.');
    if (!day || !month || !year || !timePart) return null;

    return `${year}-${month}-${day}T${timePart}`;
  }

}
