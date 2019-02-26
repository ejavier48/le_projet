import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', loadChildren: './home/home.module#HomePageModule' },
  //{ path: 'consulta/:ipAdd/:port', loadChildren: './consulta/consulta.module#ConsultaPageModule' },
  { path: 'menu/:ipAdd/:port', loadChildren: './menu/menu.module#MenuPageModule' },
  { path: 'ver-agente/:indice', loadChildren: './ver-agente/ver-agente.module#VerAgentePageModule' },
  //{ path: 'modal-interfaces', loadChildren: './modal-interfaces/modal-interfaces.module#ModalInterfacesPageModule' }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
