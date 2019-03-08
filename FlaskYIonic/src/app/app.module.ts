import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { RouteReuseStrategy } from '@angular/router';

import { IonicModule, IonicRouteStrategy } from '@ionic/angular';
import { SplashScreen } from '@ionic-native/splash-screen/ngx';
import { StatusBar } from '@ionic-native/status-bar/ngx';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';

//para usar los Modals
import { ModalController } from '@ionic/angular';

//Para hacer peticiones a Flask
import { HttpClientModule } from '@angular/common/http';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';

//Servicio que hize para conectar con Flask
import { MensajeroFlaskService } from './mensajero-flask.service';
//Pagina a mandar a llamar a los Modals
import { ModalInterfacesPage } from "./modal-interfaces/modal-interfaces.page"


//Para guardar informacion de manera permanente
import { IonicStorageModule } from '@ionic/storage';


@NgModule({
  declarations: [AppComponent,ModalInterfacesPage],
  entryComponents: [ModalInterfacesPage],
  imports: [BrowserModule, IonicModule.forRoot(), AppRoutingModule,HttpClientModule, IonicStorageModule.forRoot()],
  providers: [
    StatusBar,
    SplashScreen,
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },HttpClient,
    MensajeroFlaskService, ModalController

  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
