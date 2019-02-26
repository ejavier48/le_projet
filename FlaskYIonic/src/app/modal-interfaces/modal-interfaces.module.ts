import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Routes, RouterModule } from '@angular/router';

import { IonicModule } from '@ionic/angular';

import { ModalInterfacesPage } from './modal-interfaces.page';

const routes: Routes = [
  {
    path: '',
    component: ModalInterfacesPage
  }
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RouterModule.forChild(routes)
  ],
  declarations: [ModalInterfacesPage]
})
export class ModalInterfacesPageModule {}
