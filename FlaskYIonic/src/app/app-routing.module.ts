import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', loadChildren: './home/home.module#HomePageModule' },
  //{ path: 'consulta/:ipAdd/:port', loadChildren: './consulta/consulta.module#ConsultaPageModule' },
  { path: 'menu/:ipAdd/:port', loadChildren: './menu/menu.module#MenuPageModule' }

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
