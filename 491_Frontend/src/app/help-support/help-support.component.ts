import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-help-support',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './help-support.component.html',
  styleUrls: ['./help-support.component.css']
})

export class HelpSupportComponent implements OnInit {

  email: string = '';
  userMessage: string = '';
  submitMessage: string = '';

  faqs: any[] = [];

  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.loadFAQs();
  }

  loadFAQs(): void {
    this.apiService.getFAQs().subscribe({
      next: (res) => {
        console.log('[FAQ] Veriler:', res);
        this.faqs = res;
      },
      error: (err) => {
        console.error('[FAQ] Hata:', err);
      }
    });
  }

  goToMainMenu(): void {
    this.router.navigate(['/mainMenu']);
  }

  submitSupport(): void {
    console.log('[submitSupport] Fonksiyon çağrıldı');
  
    this.submitMessage = '';
  
    const trimmedEmail = this.email?.trim();
    const trimmedMessage = this.userMessage?.trim();
  
    console.log('[submitSupport] Email:', trimmedEmail);
    console.log('[submitSupport] Mesaj:', trimmedMessage);
  
    if (!trimmedEmail || !trimmedMessage) {
      this.submitMessage = 'Lütfen e‑posta ve mesaj alanlarını doldurun.';
      console.warn('[submitSupport] Boş alan hatası');
      return;
    }
  
    const payload = {
      email: trimmedEmail,
      message: trimmedMessage
    };
  
    console.log('[submitSupport] Gönderilecek payload:', payload);
  
    this.apiService.submitSupportMessage(payload).subscribe({
      next: (res) => {
        console.log('[submitSupport] API başarılı:', res);
        this.submitMessage = 'Mesajınız başarıyla gönderildi.';
  
        this.email = '';
        this.userMessage = '';
      },
      error: (err) => {
        console.error('[submitSupport] API hatası:', err);
        this.submitMessage = 'Mesaj gönderilirken bir hata oluştu.';
      }
    });
  }

}
