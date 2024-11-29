import { Component, NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MainMenuComponent } from './main-menu/main-menu.component';
import { ManagementPanelComponent } from './management-panel/management-panel.component';
import { HelpSupportComponent } from './help-support/help-support.component';
import { AdminPanelComponent } from './admin-panel/admin-panel.component';
import { ManagementPanelLoginComponent } from './management-panel-login/management-panel-login.component';
import path from 'path';


export const routes: Routes = [
    {path: '', component: MainMenuComponent},
    {path: 'mainMenu', component: MainMenuComponent},
    { path: 'managementPanel', component: ManagementPanelComponent },
    { path: 'helpSupport', component: HelpSupportComponent },
    { path: 'adminPanel', component: AdminPanelComponent },
    { path: 'managementPanelLogin', component: ManagementPanelLoginComponent },


    {path: '**', redirectTo: 'mainMenu'}
];

