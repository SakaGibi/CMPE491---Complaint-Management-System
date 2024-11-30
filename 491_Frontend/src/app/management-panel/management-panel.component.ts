import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-management-panel',
  imports: [CommonModule], // CommonModule'u buraya ekleyin
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent {
  isDetailsModalOpen = false;
  currentDetailsType: 'chart' | 'graph' | null = null;

  openDetails(type: 'chart' | 'graph') {
    this.currentDetailsType = type;
    this.isDetailsModalOpen = true;
  }

  closeDetails() {
    this.isDetailsModalOpen = false;
    this.currentDetailsType = null;
  }
}
