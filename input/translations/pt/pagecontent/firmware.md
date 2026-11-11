O [firmware](https://github.com/costateixeira/spenser/tree/master/firmware) corre num **dispensador baseado em ESP32-S3** que usa o [M5Stack AtomS3 Lite](https://shop.m5stack.com/products/atoms3-lite) e o [M5Stack Atomic Motion Base](https://shop.m5stack.com/products/atomic-motion), concebido para dispensar chocolate ao receber `MedicationRequest`s FHIR por HTTP.

Suporta:
- Um portal local de configuração de Wi-Fi (através de portal cativo ou do botão)
- Endpoints RESTful para interação FHIR
  - 📦 `InventoryReport` FHIR para comunicar (GET) e ajustar (POST) o inventário
  - 🏥 Aceitar recursos `MedicationRequest` por HTTP POST e responder com `MedicationDispense`
- Serviços RESTful para depuração e gestão do inventário

### Utilização
1. Instale o PlatformIO - Nota: o VSCode funciona, o VSCodium não
2. Ligue a uma porta USB. No Windows, use os controladores da Microsoft - **NÃO use outros controladores como CH340 etc.**
3. A partir da pasta `firmware`, execute o PlatformIo para compilar, carregar e monitorizar
4. **Ajude a melhorar o código - os PR são mais do que bem-vindos.**


---

### 🌐 Endpoints FHIR

Estes endpoints estão em conformidade com o [FHIR R5](https://hl7.org/fhir/R5):

#### `GET /metadata`
- Devolve uma `CapabilityStatement` FHIR
- Declara o suporte para os recursos FHIR

#### `POST /MedicationRequest`
- Aceita um recurso FHIR `MedicationRequest` (JSON)
- Dispensa chocolate negro ou de leite, conforme o código do medicamento
- Responde com um recurso `MedicationDispense`
- Se não houver stock, responde com uma `MedicationDispense` recusada

#### `POST /InventoryReport`
- Aceita um recurso FHIR `InventoryReport`
- Suporta:
  - `countType: snapshot` — substitui o inventário
  - `countType: difference` — ajusta o inventário de forma incremental
- Valida as restrições do inventário (por exemplo, sem valores negativos)
- Responde com o inventário atualizado ou com um erro

#### `GET /InventoryReport`
- Devolve um `InventoryReport` do tipo snapshot que representa o stock atual
- Inclui as localizações e o estado dos artigos

---

### ⚙️ Endpoints de configuração e depuração

Estes são endpoints utilitários para diagnóstico, configuração e testes interativos.

#### Configuração de Wi-Fi

| Endpoint                      | Descrição                                       |
|------------------------------|---------------------------------------------------|
| `GET /wifi-settings`         | Marca o dispositivo para entrar no modo de configuração de Wi-Fi ao reiniciar |
| `GET /wifi-reboot-config`    | Reinicia imediatamente no modo de configuração              |
| `GET /wifi-reset`            | Limpa as credenciais de Wi-Fi guardadas                   |
| `GET /startConfig`           | Aciona o modo de configuração de Wi-Fi e reinicia              |
| `GET /wifi`                  | Redireciona para o portal de configuração se não houver ligação       |

#### Interface e informação

| Endpoint            | Descrição                                      |
|---------------------|--------------------------------------------------|
| `GET /`             | Serve a interface a partir de SPIFFS ou redireciona no modo AP     |
| `GET /ui.html`      | Serve a interface estática (`index.html`)                  |
| `GET /success`      | Ecrã de confirmação após a configuração de Wi-Fi           |
| `GET /ip-info`      | Mostra o IP e redireciona automaticamente para ele                 |

#### Depuração e controlo manual {#debugging--manual-control}

| Endpoint            | Descrição                                     |
|---------------------|-------------------------------------------------|
| `GET /setColor`     | Altera a cor do LED RGB através de parâmetros de consulta       |
| `GET /setServos`    | Define os ângulos dos servos através de parâmetros de consulta               |
| `GET /reset`        | Repõe o LED e os dois servos a 0                  |
| `GET /flashServo1`  | Leva brevemente o servo 1 a `dispenseAngle`        |
| `GET /flashServo2`  | Leva brevemente o servo 2 a `dispenseAngle`        |
| `GET /inventory`    | Mostra os níveis atuais de inventário em JSON           |
| `GET /resetInventory?dark=10&milk=15` | Define manualmente as contagens de inventário     |
| `GET /battery`      | Comunica a tensão e a percentagem da bateria           |

#### Compatibilidade com portais cativos

Estes endpoints redirecionam para `/success`, para lidar com os portais cativos específicos de cada plataforma:

- `/generate_204`
- `/hotspot-detect.html`
- `/fwlink`
- `/connecttest.txt`
- `/ncsi.txt`
- `/i`



---

### 🚀 Wi-Fi e arranque
Sem credenciais guardadas, o firmware serve o seu próprio ponto de acesso aberto, com o nome `Spenser-` seguido dos dois últimos bytes do seu endereço MAC, em `192.168.4.1`. Ao ligar-se a essa rede, a página de configuração abre sozinha; a partir dela indica-se à unidade a rede a que se deve ligar, e essas credenciais mantêm-se entre arranques.  
Uma vez ligada a uma rede, fica acessível em [http://spenser.local](http://spenser.local), que anuncia por mDNS como `spenser`.  
Ver [Configurar uma unidade](setup.html).


---

### 🔋 Comportamento do hardware

- **Pino do botão:** GPIO 41
  - Manter premido 3 segundos durante o arranque: entra no modo de configuração de Wi-Fi
  - Pressão curta durante o funcionamento: dispensa um chocolate negro - **também conhecido como PANIC ! / Hit Me !!**
- **Pino do LED RGB:** GPIO 35 (WS2812)
- **Servos:**
  - Servo 0: chocolate negro
  - Servo 1: chocolate de leite
  - `dispenseAngle` predefinido: 97°

---





### 📦 Armazenamento

- **SPIFFS** é usado para servir `index.html` e os recursos da interface.
- **Preferences** é usado para persistir o sinalizador `forceConfig` para a configuração de Wi-Fi.

---

### 🔋 Monitorização da bateria

(Em desenvolvimento / os resultados podem variar) 
- Lê a tensão do sensor INA226 no Atomic Motion Base.
- Estima a % da bateria através de um ajuste polinomial.
- Consulte o estado da bateria com [`GET /battery`](#debugging--manual-control)

---

### 🧪 Testes manuais

Use estes endpoints para testar a funcionalidade:

- `GET /flashServo1` — Dispensa chocolate negro manualmente
- `GET /flashServo2` — Dispensa chocolate de leite manualmente
- `GET /setColor?red=0&green=255&blue=0` — Coloca o LED a verde
- `GET /resetInventory?dark=20&milk=20` — Repõe o inventário

---

### ✅ Exemplo de POST de `MedicationRequest`

```json
{
  "resourceType": "MedicationRequest",
  "id": "req-123",
  "status": "active",
  "intent": "instance-order",
  "medicationCodeableConcept": {
    "coding": [
      {
        "code": "chocolate-dark",
        "display": "Dark Chocolate"
      }
    ]
  },
  "dosageInstruction": [
    { "text": "Dispense one dark chocolate" }
  ],
  "subject": { "reference": "Patient/example" }
}
```

