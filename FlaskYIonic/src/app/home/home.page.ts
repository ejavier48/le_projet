import { Component } from '@angular/core';

//para poder moverme entre pantallas
import { Router } from "@angular/router";


@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
})
export class HomePage {
  ipAdd:string;
  port:string;
  showAlert: boolean;
  constructor(private router: Router){
    this.showAlert = false;
    this.ipAdd="";
    this.port="";
  }

  irAConsulta(){
    if(this.ipAdd=="" || this.port==""){
      console.log(this.ipAdd);
      console.log(this.port);
      console.log("error");
      this.showAlert = true;


    }
    else{
      this.router.navigate(['/menu',this.ipAdd, this.port,'menu','menu','consulta',this.ipAdd, this.port]);
      this.showAlert = false ;
      
    }



  }



}
