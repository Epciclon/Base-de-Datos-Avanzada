/*==============================================================*/
/* DBMS name:      PostgreSQL 8                                 */
/* Created on:     31/07/2025 14:39:23                          */
/*==============================================================*/

/*==============================================================*/
/* Table: BOUCHER_CABECERA                                      */
/*==============================================================*/
create table BOUCHER_CABECERA (
   BAN_AID              VARCHAR(14)          not null,
   BAN_NOMBRE           VARCHAR(64)          not null,
   BAN_DIRECCION        VARCHAR(64)          not null,
   BAN_RUC              VARCHAR(13)          not null,
   BAN_MENSAJE          VARCHAR(300)         not null,
   constraint PK_BOUCHER_CABECERA primary key (BAN_AID)
);

/*==============================================================*/
/* Index: BOUCHER_CABECERA_PK                                   */
/*==============================================================*/
create unique index BOUCHER_CABECERA_PK on BOUCHER_CABECERA (
BAN_AID
);

/*==============================================================*/
/* Table: BOUCHER_CUERPO                                        */
/*==============================================================*/
create table BOUCHER_CUERPO (
   BOUC_ID              INT4                 not null,
   RETT_IMPRIMIR        VARCHAR(2)           not null,
   RETT_MONTOMAX        INT4                 not null,
   TRAN_ID              INT4                 not null,
   RET_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   RET_FECHA            DATE                 not null,
   RET_MONTO            INT4                 not null,
   RET_CAJERO           VARCHAR(8)           not null,
   RET_NUMERO_TRAN      VARCHAR(4)           not null,
   BAN_AID              VARCHAR(14)          not null,
   BOUC_COSTO           DECIMAL              not null,
   BOUC_TOTALDEBITADO   DECIMAL              not null,
   constraint PK_BOUCHER_CUERPO primary key (BOUC_ID, TRAN_ID, RET_ID)
);

/*==============================================================*/
/* Index: BOUCHER_CUERPO_PK                                     */
/*==============================================================*/
create unique index BOUCHER_CUERPO_PK on BOUCHER_CUERPO (
BOUC_ID,
TRAN_ID,
RET_ID
);

/*==============================================================*/
/* Index: CABECERA_CUERPO_FK                                    */
/*==============================================================*/
create  index CABECERA_CUERPO_FK on BOUCHER_CUERPO (
BAN_AID
);

/*==============================================================*/
/* Index: HERENCIABOUCHER_FK                                    */
/*==============================================================*/
create  index HERENCIABOUCHER_FK on BOUCHER_CUERPO (
TRAN_ID,
RET_ID
);

/*==============================================================*/
/* Table: CAJERO                                                */
/*==============================================================*/
create table CAJERO (
   CAJ_ID               INT4                 not null,
   CAJ_UBICACION        VARCHAR(100)         not null,
   CAJ_ESTADO           VARCHAR(20)          not null,
   CAJ_TIPO             VARCHAR(30)          not null,
   CAJ_SUCURSAL         VARCHAR(50)          not null,
   constraint PK_CAJERO primary key (CAJ_ID)
);

/*==============================================================*/
/* Index: CAJERO_PK                                             */
/*==============================================================*/
create unique index CAJERO_PK on CAJERO (
CAJ_ID
);

/*==============================================================*/
/* Table: CLIENTE                                               */
/*==============================================================*/
create table CLIENTE (
   PER_ID               INT4                 not null,
   CLI_ID               INT4                 not null,
   PER_NOMBRES          VARCHAR(300)         not null,
   PER_APELLIDOS        VARCHAR(300)         not null,
   PER_FECHA_NACIMIENTO DATE                 not null,
   PER_GENERO           VARCHAR(64)          not null,
   PER_TELEFONO         VARCHAR(10)          not null,
   PER_CORREO           VARCHAR(64)          not null,
   PER_DIRECCION        VARCHAR(124)         not null,
   PER_TIPO             VARCHAR(64)          not null,
   CLI_FECHA_INGRESP    DATE                 not null,
   CLI_ESTADO           VARCHAR(64)          not null,
   constraint PK_CLIENTE primary key (PER_ID, CLI_ID)
);

/*==============================================================*/
/* Index: CLIENTE_PK                                            */
/*==============================================================*/
create unique index CLIENTE_PK on CLIENTE (
PER_ID,
CLI_ID
);

/*==============================================================*/
/* Index: HERENCIACLIENTE_FK                                    */
/*==============================================================*/
create  index HERENCIACLIENTE_FK on CLIENTE (
PER_ID
);

/*==============================================================*/
/* Table: CONDICIONES                                           */
/*==============================================================*/
create table CONDICIONES (
   COND_ID              INT4                 not null,
   COND_DESCRIPCION     VARCHAR(200)         not null,
   COND_HORAS           INT4                 not null,
   COND_INTENTOS        INT4                 not null,
   COND_MONTO           INT4                 not null,
   COND_ESTADO          VARCHAR(20)          not null,
   constraint PK_CONDICIONES primary key (COND_ID)
);

/*==============================================================*/
/* Index: CONDICIONES_PK                                        */
/*==============================================================*/
create unique index CONDICIONES_PK on CONDICIONES (
COND_ID
);

/*==============================================================*/
/* Table: CONSULTA                                              */
/*==============================================================*/
create table CONSULTA (
   TRAN_ID              INT4                 not null,
   CONS_ID              INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   CONS_FECHA_HORA      DATE                 not null,
   CONS_COMISION        DECIMAL              not null,
   CONS_TIPO            VARCHAR(100)         not null,
   CONS_RESULTADOS      TEXT                 not null,
   constraint PK_CONSULTA primary key (TRAN_ID, CONS_ID)
);

/*==============================================================*/
/* Index: CONSULTA_PK                                           */
/*==============================================================*/
create unique index CONSULTA_PK on CONSULTA (
TRAN_ID,
CONS_ID
);

/*==============================================================*/
/* Index: HERENCIATRANSACCION_FK                                */
/*==============================================================*/
create  index HERENCIATRANSACCION_FK on CONSULTA (
TRAN_ID
);

/*==============================================================*/
/* Table: CUENTA                                                */
/*==============================================================*/
create table CUENTA (
   CUEN_ID              INT4                 not null,
   PER_ID               INT4                 not null,
   CLI_ID               INT4                 not null,
   CUEN_USUARIO         VARCHAR(64)          not null,
   CUEN_PASSWORD        VARCHAR(64)          not null,
   CUEN_TIPO            VARCHAR(64)          not null,
   CUEN_NUMERO_CUENTA   VARCHAR(10)          not null,
   CUEN_SALDO           DECIMAL              not null,
   CUEN_ESTADO          VARCHAR(64)          not null,
   constraint PK_CUENTA primary key (CUEN_ID)
);

/*==============================================================*/
/* Index: CUENTA_PK                                             */
/*==============================================================*/
create unique index CUENTA_PK on CUENTA (
CUEN_ID
);

/*==============================================================*/
/* Index: CUENTA_CLIENTE_FK                                     */
/*==============================================================*/
create  index CUENTA_CLIENTE_FK on CUENTA (
PER_ID,
CLI_ID
);

/*==============================================================*/
/* Table: CUENTA_AHORRO                                         */
/*==============================================================*/
create table CUENTA_AHORRO (
   CUEN_ID              INT4                 not null,
   PER_ID               INT4                 null,
   CLI_ID               INT4                 not null,
   CUEN_USUARIO         VARCHAR(64)          not null,
   CUEN_PASSWORD        VARCHAR(64)          not null,
   CUEN_TIPO            VARCHAR(64)          not null,
   CUEN_NUMERO_CUENTA   VARCHAR(10)          not null,
   CUEN_SALDO           DECIMAL              not null,
   CUEN_ESTADO          VARCHAR(64)          not null,
   CA_INTERES           DECIMAL              not null,
   CA_LIMITE_RETIROS    INT4                 not null,
   CA_MIN_SALDO_REMUNERADO DECIMAL              not null,
   constraint PK_CUENTA_AHORRO primary key (CUEN_ID)
);

/*==============================================================*/
/* Index: CUENTA_AHORRO_PK                                      */
/*==============================================================*/
create unique index CUENTA_AHORRO_PK on CUENTA_AHORRO (
CUEN_ID
);

/*==============================================================*/
/* Table: CUENTA_CORRIENTE                                      */
/*==============================================================*/
create table CUENTA_CORRIENTE (
   CUEN_ID              INT4                 not null,
   PER_ID               INT4                 null,
   CLI_ID               INT4                 not null,
   CUEN_USUARIO         VARCHAR(64)          not null,
   CUEN_PASSWORD        VARCHAR(64)          not null,
   CUEN_TIPO            VARCHAR(64)          not null,
   CUEN_NUMERO_CUENTA   VARCHAR(10)          not null,
   CUEN_SALDO           DECIMAL              not null,
   CUEN_ESTADO          VARCHAR(64)          not null,
   CC_LIMITE_DESCUBIERTO DECIMAL              not null,
   CC_COMISION_MANTENIMIENTO DECIMAL              not null,
   CC_NUM_CHEQUES       INT4                 not null,
   constraint PK_CUENTA_CORRIENTE primary key (CUEN_ID)
);

/*==============================================================*/
/* Index: CUENTA_CORRIENTE_PK                                   */
/*==============================================================*/
create unique index CUENTA_CORRIENTE_PK on CUENTA_CORRIENTE (
CUEN_ID
);

/*==============================================================*/
/* Table: DEPOSITOS                                             */
/*==============================================================*/
create table DEPOSITOS (
   TRAN_ID              INT4                 not null,
   DEP_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   DEP_FECHA            DATE                 not null,
   DEP_MONTO            DECIMAL              not null,
   DEP_CUENTA_DEST      VARCHAR(20)          not null,
   DEP_CANAL            VARCHAR(20)          not null,
   DEP_REFERENCIA       VARCHAR(30)          not null,
   DEP_ESTADO           VARCHAR(20)          not null,
   constraint PK_DEPOSITOS primary key (TRAN_ID, DEP_ID)
);

/*==============================================================*/
/* Index: DEPOSITOS_PK                                          */
/*==============================================================*/
create unique index DEPOSITOS_PK on DEPOSITOS (
TRAN_ID,
DEP_ID
);

/*==============================================================*/
/* Index: HERENCIATRANSACCION3_FK                               */
/*==============================================================*/
create  index HERENCIATRANSACCION3_FK on DEPOSITOS (
TRAN_ID
);

/*==============================================================*/
/* Table: PAGO_SERVICIOS                                        */
/*==============================================================*/
create table PAGO_SERVICIOS (
   TRAN_ID              INT4                 not null,
   PS_ID                INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   PS_TIPO_SERVICIO     VARCHAR(100)         not null,
   PS_PROVEEDOR         VARCHAR(100)         not null,
   PS_REFERENCIA        VARCHAR(100)         not null,
   PS_MONTO             DECIMAL              not null,
   PS_FECHA_HORA        DATE                 not null,
   PS_COMISION          DECIMAL              not null,
   PS_RESULTADO_CODIGO  VARCHAR(10)          not null,
   PS_ESTADO            VARCHAR(20)          not null,
   PS_COMPROBANTE       TEXT                 not null,
   constraint PK_PAGO_SERVICIOS primary key (TRAN_ID, PS_ID)
);

/*==============================================================*/
/* Index: PAGO_SERVICIOS_PK                                     */
/*==============================================================*/
create unique index PAGO_SERVICIOS_PK on PAGO_SERVICIOS (
TRAN_ID,
PS_ID
);

/*==============================================================*/
/* Index: HERENCIATRANSACCION2_FK                               */
/*==============================================================*/
create  index HERENCIATRANSACCION2_FK on PAGO_SERVICIOS (
TRAN_ID
);

/*==============================================================*/
/* Table: PERSONA                                               */
/*==============================================================*/
create table PERSONA (
   PER_ID               INT4                 not null,
   PER_NOMBRES          VARCHAR(300)         not null,
   PER_APELLIDOS        VARCHAR(300)         not null,
   PER_FECHA_NACIMIENTO DATE                 not null,
   PER_GENERO           VARCHAR(64)          not null,
   PER_TELEFONO         VARCHAR(10)          not null,
   PER_CORREO           VARCHAR(64)          not null,
   PER_DIRECCION        VARCHAR(124)         not null,
   PER_TIPO             VARCHAR(64)          not null,
   constraint PK_PERSONA primary key (PER_ID)
);

/*==============================================================*/
/* Index: PERSONA_PK                                            */
/*==============================================================*/
create unique index PERSONA_PK on PERSONA (
PER_ID
);

/*==============================================================*/
/* Table: PERSONA_JURIDICA                                      */
/*==============================================================*/
create table PERSONA_JURIDICA (
   PER_ID               INT4                 not null,
   PER_NOMBRES          VARCHAR(300)         not null,
   PER_APELLIDOS        VARCHAR(300)         not null,
   PER_FECHA_NACIMIENTO DATE                 not null,
   PER_GENERO           VARCHAR(64)          not null,
   PER_TELEFONO         VARCHAR(10)          not null,
   PER_CORREO           VARCHAR(64)          not null,
   PER_DIRECCION        VARCHAR(124)         not null,
   PER_TIPO             VARCHAR(64)          not null,
   PJ_RUC               VARCHAR(13)          not null,
   PJ_REPRESENTANTE     VARCHAR(100)         not null,
   PJ_TIPO_ENTIDAD      VARCHAR(50)          not null,
   PJ_FECHA_CONSTITUCION DATE                 not null,
   PJ_ACTIVIDAD         VARCHAR(200)         not null,
   constraint PK_PERSONA_JURIDICA primary key (PER_ID)
);

/*==============================================================*/
/* Index: PERSONA_JURIDICA_PK                                   */
/*==============================================================*/
create unique index PERSONA_JURIDICA_PK on PERSONA_JURIDICA (
PER_ID
);

/*==============================================================*/
/* Table: PERSONA_NATURAL                                       */
/*==============================================================*/
create table PERSONA_NATURAL (
   PER_ID               INT4                 not null,
   PER_NOMBRES          VARCHAR(300)         not null,
   PER_APELLIDOS        VARCHAR(300)         not null,
   PER_FECHA_NACIMIENTO DATE                 not null,
   PER_GENERO           VARCHAR(64)          not null,
   PER_TELEFONO         VARCHAR(10)          not null,
   PER_CORREO           VARCHAR(64)          not null,
   PER_DIRECCION        VARCHAR(124)         not null,
   PER_TIPO             VARCHAR(64)          not null,
   PN_IDENTIFICACION    VARCHAR(13)          not null,
   PN_ESTADO_CIVIL      VARCHAR(20)          not null,
   PN_PROFESION         VARCHAR(100)         not null,
   constraint PK_PERSONA_NATURAL primary key (PER_ID)
);

/*==============================================================*/
/* Index: PERSONA_NATURAL_PK                                    */
/*==============================================================*/
create unique index PERSONA_NATURAL_PK on PERSONA_NATURAL (
PER_ID
);

/*==============================================================*/
/* Table: RETIRO                                                */
/*==============================================================*/
create table RETIRO (
   TRAN_ID              INT4                 not null,
   RET_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   RET_FECHA            DATE                 not null,
   RET_MONTO            INT4                 not null,
   RET_CAJERO           VARCHAR(8)           not null,
   RET_NUMERO_TRAN      VARCHAR(4)           not null,
   constraint PK_RETIRO primary key (TRAN_ID, RET_ID)
);

/*==============================================================*/
/* Index: RETIRO_PK                                             */
/*==============================================================*/
create unique index RETIRO_PK on RETIRO (
TRAN_ID,
RET_ID
);

/*==============================================================*/
/* Index: HERENCIATRANSACCION5_FK                               */
/*==============================================================*/
create  index HERENCIATRANSACCION5_FK on RETIRO (
TRAN_ID
);

/*==============================================================*/
/* Table: RETIRO_CONTARJETA                                     */
/*==============================================================*/
create table RETIRO_CONTARJETA (
   TRAN_ID              INT4                 not null,
   RET_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   RET_FECHA            DATE                 not null,
   RET_MONTO            INT4                 not null,
   RET_CAJERO           VARCHAR(8)           not null,
   RET_NUMERO_TRAN      VARCHAR(4)           not null,
   RETT_IMPRIMIR        VARCHAR(2)           not null,
   RETT_MONTOMAX        INT4                 not null,
   constraint PK_RETIRO_CONTARJETA primary key (TRAN_ID, RET_ID)
);

/*==============================================================*/
/* Index: RETIRO_CONTARJETA_PK                                  */
/*==============================================================*/
create unique index RETIRO_CONTARJETA_PK on RETIRO_CONTARJETA (
TRAN_ID,
RET_ID
);

/*==============================================================*/
/* Table: RETIRO_SINTARJETA                                     */
/*==============================================================*/
create table RETIRO_SINTARJETA (
   TRAN_ID              INT4                 not null,
   RET_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   RET_FECHA            DATE                 not null,
   RET_MONTO            INT4                 not null,
   RET_CAJERO           VARCHAR(8)           not null,
   RET_NUMERO_TRAN      VARCHAR(4)           not null,
   COND_ID              INT4                 not null,
   RETS_CODIGO          VARCHAR(8)           not null,
   RETS_TELEFONO_ASOCIADO VARCHAR(10)          not null,
   RETS_ESTADO_CODIGO   VARCHAR(64)          not null,
   constraint PK_RETIRO_SINTARJETA primary key (TRAN_ID, RET_ID)
);

/*==============================================================*/
/* Index: RETIRO_SINTARJETA_PK                                  */
/*==============================================================*/
create unique index RETIRO_SINTARJETA_PK on RETIRO_SINTARJETA (
TRAN_ID,
RET_ID
);

/*==============================================================*/
/* Index: CONDICIONES_TARJETA_FK                                */
/*==============================================================*/
create  index CONDICIONES_TARJETA_FK on RETIRO_SINTARJETA (
COND_ID
);

/*==============================================================*/
/* Table: TARJETA                                               */
/*==============================================================*/
create table TARJETA (
   TAR_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   TAR_NUMERO_TARJETA   VARCHAR(16)          not null,
   TAR_FECHA_EMISION    DATE                 not null,
   TAR_FECHA_EXPIRACION DATE                 not null,
   TAR_ESTADO_TARJETA   VARCHAR(64)          not null,
   TAR_CVV              VARCHAR(3)           not null,
   TAR_TIPO             VARCHAR(64)          not null,
   TAR_PIN              VARCHAR(4)           not null,
   constraint PK_TARJETA primary key (TAR_ID)
);

/*==============================================================*/
/* Index: TARJETA_PK                                            */
/*==============================================================*/
create unique index TARJETA_PK on TARJETA (
TAR_ID
);

/*==============================================================*/
/* Index: CUENTA_TARJETA_FK                                     */
/*==============================================================*/
create  index CUENTA_TARJETA_FK on TARJETA (
CUEN_ID
);

/*==============================================================*/
/* Table: TARJETA_CREDITO                                       */
/*==============================================================*/
create table TARJETA_CREDITO (
   TAR_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   TAR_NUMERO_TARJETA   VARCHAR(16)          not null,
   TAR_FECHA_EMISION    DATE                 not null,
   TAR_FECHA_EXPIRACION DATE                 not null,
   TAR_ESTADO_TARJETA   VARCHAR(64)          not null,
   TAR_CVV              VARCHAR(3)           not null,
   TAR_TIPO             VARCHAR(64)          not null,
   TAR_PIN              VARCHAR(4)           not null,
   TC_LIMITE_CREDITO    DECIMAL              not null,
   TC_TASA_INTERES      DECIMAL              not null,
   TC_CARGO_ANUAL       DECIMAL              not null,
   TC_FECHA_CORTE       DATE                 not null,
   TC_FECHA_VENCIMIENTO DATE                 not null,
   TC_MOROSIDAD         BOOL                 not null,
   constraint PK_TARJETA_CREDITO primary key (TAR_ID)
);

/*==============================================================*/
/* Index: TARJETA_CREDITO_PK                                    */
/*==============================================================*/
create unique index TARJETA_CREDITO_PK on TARJETA_CREDITO (
TAR_ID
);

/*==============================================================*/
/* Table: TARJETA_DEBITO                                        */
/*==============================================================*/
create table TARJETA_DEBITO (
   TAR_ID               INT4                 not null,
   CUEN_ID              INT4                 not null,
   TAR_NUMERO_TARJETA   VARCHAR(16)          not null,
   TAR_FECHA_EMISION    DATE                 not null,
   TAR_FECHA_EXPIRACION DATE                 not null,
   TAR_ESTADO_TARJETA   VARCHAR(64)          not null,
   TAR_CVV              VARCHAR(3)           not null,
   TAR_TIPO             VARCHAR(64)          not null,
   TAR_PIN              VARCHAR(4)           not null,
   TD_LIMITE_RETIRO_DIARIO DECIMAL              not null,
   TD_COMISION_SOBREGIRO DECIMAL              not null,
   constraint PK_TARJETA_DEBITO primary key (TAR_ID)
);

/*==============================================================*/
/* Index: TARJETA_DEBITO_PK                                     */
/*==============================================================*/
create unique index TARJETA_DEBITO_PK on TARJETA_DEBITO (
TAR_ID
);

/*==============================================================*/
/* Table: TRANSACCION                                           */
/*==============================================================*/
create table TRANSACCION (
   TRAN_ID              INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   constraint PK_TRANSACCION primary key (TRAN_ID)
);

/*==============================================================*/
/* Index: TRANSACCION_PK                                        */
/*==============================================================*/
create unique index TRANSACCION_PK on TRANSACCION (
TRAN_ID
);

/*==============================================================*/
/* Index: CUENTA_TRANSACCION_FK                                 */
/*==============================================================*/
create  index CUENTA_TRANSACCION_FK on TRANSACCION (
CUEN_ID
);

/*==============================================================*/
/* Index: TRANSACCION_CAJERO_FK                                 */
/*==============================================================*/
create  index TRANSACCION_CAJERO_FK on TRANSACCION (
CAJ_ID
);

/*==============================================================*/
/* Table: TRANSFERENCIA                                         */
/*==============================================================*/
create table TRANSFERENCIA (
   TRAN_ID              INT4                 not null,
   TRANS_ID             INT4                 not null,
   CUEN_ID              INT4                 not null,
   CAJ_ID               INT4                 not null,
   TRANS_FECHA          DATE                 not null,
   TRANS_MONTO          DECIMAL              not null,
   TRANS_ORIGEN         VARCHAR(20)          not null,
   TRANS_DESTINO        VARCHAR(20)          not null,
   TRANS_CANAL          VARCHAR(20)          not null,
   TRANS_ESTADO         VARCHAR(20)          not null,
   constraint PK_TRANSFERENCIA primary key (TRAN_ID, TRANS_ID)
);

/*==============================================================*/
/* Index: TRANSFERENCIA_PK                                      */
/*==============================================================*/
create unique index TRANSFERENCIA_PK on TRANSFERENCIA (
TRAN_ID,
TRANS_ID
);

/*==============================================================*/
/* Index: HERENCIATRANSACCION4_FK                               */
/*==============================================================*/
create  index HERENCIATRANSACCION4_FK on TRANSFERENCIA (
TRAN_ID
);

alter table BOUCHER_CUERPO
   add constraint FK_BOUCHER__CABECERA__BOUCHER_ foreign key (BAN_AID)
      references BOUCHER_CABECERA (BAN_AID)
      on delete restrict on update restrict;

alter table BOUCHER_CUERPO
   add constraint FK_BOUCHER__HERENCIAB_RETIRO_C foreign key (TRAN_ID, RET_ID)
      references RETIRO_CONTARJETA (TRAN_ID, RET_ID)
      on delete restrict on update restrict;

alter table CLIENTE
   add constraint FK_CLIENTE_HERENCIAC_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
      on delete restrict on update restrict;

alter table CONSULTA
   add constraint FK_CONSULTA_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
      on delete restrict on update restrict;

alter table CUENTA
   add constraint FK_CUENTA_CUENTA_CL_CLIENTE foreign key (PER_ID, CLI_ID)
      references CLIENTE (PER_ID, CLI_ID)
      on delete restrict on update restrict;

alter table CUENTA_AHORRO
   add constraint FK_CUENTA_A_HERENCIAC_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
      on delete restrict on update restrict;

alter table CUENTA_CORRIENTE
   add constraint FK_CUENTA_C_HERENCIAC_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
      on delete restrict on update restrict;

alter table DEPOSITOS
   add constraint FK_DEPOSITO_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
      on delete restrict on update restrict;

alter table PAGO_SERVICIOS
   add constraint FK_PAGO_SER_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
      on delete restrict on update restrict;

alter table PERSONA_JURIDICA
   add constraint FK_PERSONA__HERENCIA4_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
      on delete restrict on update restrict;

alter table PERSONA_NATURAL
   add constraint FK_PERSONA__HERENCIA3_PERSONA foreign key (PER_ID)
      references PERSONA (PER_ID)
      on delete restrict on update restrict;

alter table RETIRO
   add constraint FK_RETIRO_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
      on delete restrict on update restrict;

alter table RETIRO_CONTARJETA
   add constraint FK_RETIRO_C_INHERITAN_RETIRO foreign key (TRAN_ID, RET_ID)
      references RETIRO (TRAN_ID, RET_ID)
      on delete restrict on update restrict;

alter table RETIRO_SINTARJETA
   add constraint FK_RETIRO_S_CONDICION_CONDICIO foreign key (COND_ID)
      references CONDICIONES (COND_ID)
      on delete restrict on update restrict;

alter table RETIRO_SINTARJETA
   add constraint FK_RETIRO_S_INHERITAN_RETIRO foreign key (TRAN_ID, RET_ID)
      references RETIRO (TRAN_ID, RET_ID)
      on delete restrict on update restrict;

alter table TARJETA
   add constraint FK_TARJETA_CUENTA_TA_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
      on delete restrict on update restrict;

alter table TARJETA_CREDITO
   add constraint FK_TARJETA__HERENCIA_TARJETA foreign key (TAR_ID)
      references TARJETA (TAR_ID)
      on delete restrict on update restrict;

alter table TARJETA_DEBITO
   add constraint FK_TARJETA__HERENCIA2_TARJETA foreign key (TAR_ID)
      references TARJETA (TAR_ID)
      on delete restrict on update restrict;

alter table TRANSACCION
   add constraint FK_TRANSACC_CUENTA_TR_CUENTA foreign key (CUEN_ID)
      references CUENTA (CUEN_ID)
      on delete restrict on update restrict;

alter table TRANSACCION
   add constraint FK_TRANSACC_TRANSACCI_CAJERO foreign key (CAJ_ID)
      references CAJERO (CAJ_ID)
      on delete restrict on update restrict;

alter table TRANSFERENCIA
   add constraint FK_TRANSFER_HERENCIAT_TRANSACC foreign key (TRAN_ID)
      references TRANSACCION (TRAN_ID)
      on delete restrict on update restrict;

