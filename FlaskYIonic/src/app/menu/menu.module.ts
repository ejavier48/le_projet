import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Routes, RouterModule } from '@angular/router';

import { IonicModule } from '@ionic/angular';

import { MenuPage } from './menu.page';

const routes: Routes = [
  {
    path: 'menu',
    component: MenuPage,
    children:[
      { path: 'add-agent', loadChildren: '../add-agent/add-agent.module#AddAgentPageModule' },
      { path: 'menu/consulta/:ipAdd/:port', loadChildren: '../consulta/consulta.module#ConsultaPageModule' },
      { path: 'administrador', loadChildren: './administrador/administrador.module#AdministradorPageModule' },
    ]
  },
  {
    path: '',
    redirectTo:'/menu/add-agent'
    //redirectTo:'menu/menu/consulta/'+MensajeroFlaskService.ipAdd+'/'+MensajeroFlaskService.puerto
  }
];

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    IonicModule,
    RouterModule.forChild(routes)
  ],
  declarations: [MenuPage]
})
export class MenuPageModule {

}
