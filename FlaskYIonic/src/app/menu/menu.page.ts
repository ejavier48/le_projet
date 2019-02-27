import { Component, OnInit } from '@angular/core';
import { Router, RouterEvent } from '@angular/router'


//para recibir paramteros
import { ActivatedRoute } from "@angular/router";
@Component({
  selector: 'app-menu',
  templateUrl: './menu.page.html',
  styleUrls: ['./menu.page.scss'],
})
export class MenuPage implements OnInit {

  ipAdd:string;
  port:string;


  pages = [
      {
        title:'Agregar agente',
        url: 'add-agent'
      },
      {
        title:'Mostrar agentes',
        url: 'menu/consulta'
      },
      {
        title:'Cerrar conexion',
        url:''
      }
  ]

  selectedPath='';
  constructor(private router: Router, private activatedRoute: ActivatedRoute) {
    this.ipAdd = this.activatedRoute.snapshot.paramMap.get('ipAdd');
    this.port = this.activatedRoute.snapshot.paramMap.get('port');
    console.log(this.ipAdd);
    console.log(this.port);
    this.pages[1].url='menu/consulta'+'/'+this.ipAdd+'/'+this.port;
    this.router.events.subscribe((event: RouterEvent)=>{
        if(event.url=='menu/consulta'){
          this.selectedPath=event.url+'/'+this.ipAdd+'/'+this.port;
        }
        else
          this.selectedPath=event.url;
    });
  }

  ngOnInit() {
  }

  ionViewDidEnter(){

  }

}
