import { Component, OnInit } from '@angular/core';
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';
//para mostrar el loading
import { LoadingController } from '@ionic/angular';
//para recibir parametros
import { ActivatedRoute } from "@angular/router";
//mostrar alerta
import { AlertController } from '@ionic/angular';


@Component({
  selector: 'app-ver-agente',
  templateUrl: './ver-agente.page.html',
  styleUrls: ['./ver-agente.page.scss'],
})
export class VerAgentePage implements OnInit {
  agente:any;
  ipAdd:string;
  urlVolver:string;
  puerto:string;
  indice:string;
  constructor(private FlaskService: MensajeroFlaskService,
     private loadcont: LoadingController,
     private activatedRoute: ActivatedRoute,
     private alertController: AlertController) {
    //this.agente = this.FlaskService.agenteConsultado;
    //console.log(this.agente);
    this.indice = this.activatedRoute.snapshot.paramMap.get('indice');
    this.ipAdd=this.FlaskService.ipAdd;
    this.puerto=this.FlaskService.puerto;
    this.urlVolver="/menu/"+this.ipAdd+"/"+this.puerto+"/menu/menu/consulta/"+this.ipAdd+"/"+this.puerto;
  }

  ionViewWillEnter(){
      this.getData()
  }

  async getData(){
    let data;
    const loading = await this.loadcont.create({
      message: 'Preguntando a los duendes de SNMP'
    });
    await loading.present();

    this.FlaskService.getData(this.FlaskService.ipAdd,this.FlaskService.puerto)
      .subscribe(res => {
        data = res.devices[this.indice]._hostName;
          console.log("data obtenida "+JSON.stringify(data));
        loading.dismiss();
      },err => {
        console.log("error:"+JSON.stringify(err));
        //this.router.navigate(['/']);
          loading.dismiss();
          this.presentAlert(JSON.stringify(err));

      });
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
  ngOnInit() {}

}
