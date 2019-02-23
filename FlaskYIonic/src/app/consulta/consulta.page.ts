import { Component, OnInit } from '@angular/core';
//para recibir paramteros
import { ActivatedRoute } from "@angular/router";
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';
//para moverme entre pantallas
import { Router } from "@angular/router";
//para mostrar el loading
import { LoadingController } from '@ionic/angular';
//mostrar alerta
import { AlertController } from '@ionic/angular';

@Component({
  selector: 'app-consulta',
  templateUrl: './consulta.page.html',
  styleUrls: ['./consulta.page.scss'],
})
export class ConsultaPage implements OnInit {
  ipAdd:string;
  port:string;
  data:any;
  weHaveData:boolean;
  areWeReady:boolean;
  numeroAgentes:number;
  agentes = [];

  constructor(private activatedRoute: ActivatedRoute,
    private FlaskService: MensajeroFlaskService,
    private router: Router,
    private loadcont: LoadingController,
    public alertController: AlertController) {
      this.weHaveData=false;
      this.areWeReady=false;
      this.numeroAgentes=0;
     }

  ionViewWillEnter(){

    this.ipAdd = this.activatedRoute.snapshot.paramMap.get('ipAdd');
    this.port = this.activatedRoute.snapshot.paramMap.get('port');
    console.log(this.ipAdd);
    console.log(this.port);

    this.getData();
  }
  ngOnInit() {

  }

  async getData() {

    const loading = await this.loadcont.create({
      message: 'Conectando'
    });
    await loading.present();

    this.FlaskService.getData(this.ipAdd,this.port)
      .subscribe(res => {
        console.log(res);
        this.data = res;


        console.log("devices: "+Object.keys(this.data.devices).length);
        if(Object.keys(this.data.devices).length!=0){

          this.weHaveData=true;
          this.numeroAgentes=Object.keys(this.data.devices).length;

          //obtengo los agentes
          for (let i = 0; i < this.numeroAgentes; i++) {
              console.log(this.data.devices[i]);
              //verifico si ya existe en el arreglo, si es asi, no lo meto
              const estaEnELaArreglo =!!this.agentes.find(agente =>agente._node === this.data.devices[i]._node)
              if(!estaEnELaArreglo){
                  this.agentes.push(this.data.devices[i]);
              }

              //checo el SO
              this.clasificarSOAgente(i);
          }


        }

          this.areWeReady=true;
          loading.dismiss();
      }, err => {
        console.log("error:"+JSON.stringify(err));
        this.router.navigate(['/']);
          loading.dismiss();
          this.presentAlert(JSON.stringify(err));

      });
  }

clasificarSOAgente(indice:number){
  if(this.agentes[indice]._os.includes('windows')|| this.agentes[indice]._os.includes('windows') ){
    this.agentes[indice]._os='1';
  }
  else if(this.agentes[indice]._os.includes('linux')|| this.agentes[indice]._os.includes('Debian') || this.agentes[indice]._os.includes('Ubuntu')){
    this.agentes[indice]._os='2';
  }
  else if(this.agentes[indice]._os.includes('OSX') || this.agentes[indice]._os.includes('Apple')){
    this.agentes[indice]._os='3';
  }
  else{
    this.agentes[indice]._os='1';
  }
}

  async presentAlert(mensaje:string) {
  const alert = await this.alertController.create({
    header: 'Error de conexion',
    subHeader: 'No se ha podido establer la conexion con el servidor',
    message: mensaje,
    buttons: ['OK']
  });

  await alert.present();
}

}
