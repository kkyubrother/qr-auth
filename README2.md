나는 파이썬 FastAPI와 python-telegram-bot으로 프로젝트를 제작하려고 한다.
아래의 내용을 읽고, 할일을 시행하라.


<사용 기술>

1. Python
2. FastAPI
3. MariaDB
4. python-telegram-bot
5. React
6. SQLAlchemy
7. Pydantic
8. Swagger

</사용 기술>

<아키텍쳐>

* 관리자 <-웹-> FastAPI 서버
* 사용자 <-텔레그램-> python-telegram-bot <-http-> FastAPI 서버

</아키텍쳐>

<스키마>
<관리자>
* id
* pw
</관리자>
<사용자>
* id(pk): integer
* name: string
* tel: string
* department: string
* is_lunch: boolean
* is_dinner: boolean
* telegram_id?: integer
</사용자>
<QR>
* code
* created_at
</QR>
<인증기록>
* code
* user_id
* created_at
</인증기록>

</스키마>


<주소>

[POST] /api/admin/login: 관리자가 ID와 PW를 전송하고  

[GET] /api/admin/user: 관리자가 등록된 사용자들을 조회합니다.
[POST] /api/admin/user: 등록된 사용자들을 조회합니다.

[GET] /api/user
[POST] /api/user
[GET] /api/user/auth
</주소>

<기능>

1. 이 서비스를 사용하는 주체는 2 종류가 있다. 관리자와 사용자이다.
2. 관리자는 사용자에 대한 정보를 추가, 조회, 변경, 삭제가 가능하다.
3. 사용자에 대한 정보는 이름, 전화번호, 부서, 직책, 점심식사여부, 저녁식사여부를 등록한다.
4. 사용자는 telegram_bot(이하, 텔레봇)을 통해서만 서비스에 접근할 수 있다.
5. 사용자는 텔레봇에 처음 접근 하면 봇과 대화하며 이름, 전화번호를 입력하고, 이 정보가 서비스에 등록되어 있으면 등록된다.
6. 사용자가 등록되며 텔레그램 아이디가 사용자 정보에 추가된다.
7. 서비스는 임의의 코드를 생성한다. 이 코드는 사용자 인증에 사용되며, 1분의 유효기간을 지닌다.
8. 사용자는 해당 코드와 텔레그램 아이디를 서비스로 전송한다.
9. 서비스는 코드가 유효기간 이내인지, 텔레그램 아이디가 사용자로 등록되었는지, 인증한 시간이 점심 또는 저녁이고 사용자가 해당 시간에 식사 여부가 참인지 판단해서 결과를 반환한다.
10. 각 인증은 기록되어 관리자가 조회할 수 있다.
11. 관리자는 고정된 아이디와 패스워드를 입력하명 일치하면 관리자로 가정한다.
12. 관리자용 api는 jwt 토큰 값도 함께 받아, 일치해야만 올바른 값을 반환한다.
13. 인증 코드는 삭제하지 않음.
14. 점심 및 저녁 시간은 환경 변수로 지정한다.
15. `/` 이하의 주소로는 웹페이지 파일을 반환하되, `/api` 아래에 백엔드 통신용 url이 위치해야 한다. `/admin`은 관리자용을 위한 웹페이지를 반환하므로, 다른 React 웹페이지 파일을 정적으로
    제공해야 한다.

</기능>

<작동방식>

<사용자 등록>

1. 관리자가 사용자 정보를 서버에 등록한다.
2. 관리자가 서버에 등록하는 사용자 정보는 `이름`, `전화번호`, `부서`, `직책`, `점심식사여부`, `저녁식사여부`이다.
3. 사용자는 텔레그램 봇을 처음 대화할 때(`/start`) 봇과 대화하며 사용자 자심의 이름과 전화번호 등을 입력한다.
4. 사용자가 봇에게 입력한 정보들 중에서 이름과 전화번호가 일치한 사용자 정보가 있으면 등록에 성공한 것으로 간주하고, 사용자 정보 DB에 텔레그램 id를 추가한다.

</사용자 등록>

<인증>

1. 웹페이지에서 서버에 코드를 주기적으로 요청하고, 그 코드를 통해 QR을 생성한다.
2. 사용자들은 봇에게 아무 메세지를 보내면 봇은 qr 스캐너가 되는 웹페이지 링크(사용자 개개인의 고유키를 포함)를 전달한다.
3. 사용자들은 해당 url로 접속하여 텔레그램 웹 뷰로 qr을 인증을 하면 그 페이지에서는 qr과 사용자 고유키를 함께 보낸다.
4. 서버에서는 qr코드, 유효한 사용자, 해당 시간 식사 여부를 확인해서 모두 일치하면 'ok'를, 아니면 '{이유}'를 적절한 상태 코드와 함께 반환한다.
5. 해당 인증 기록은 성공/실패 상관없이 서버에 기록한다.

</인증>

<관리자의 사용자 조회>

1. 관리자는 웹페이지에 하드 코딩된 id와 password 접속 권한을 얻을 수 있다.
2. 관리자는 사용자에 대한 정보를 `조회`, `추가`, `변경`, `삭제`가 가능해야 한다.

</관리자의 사용자 조회>

</작동방식>

<할 일>

1. 위 기능을 이해 하였는가? 이해하였다면 설명을 해라.전체 또는 일부에 대해 이해되지 않는가? 질문을 해라.
2. 내가 준 기능으로 완전한 구현체를 작성하라. 구현체에 대해 주석을 작성하고 이해하고 작성한 기능을 소개하라.
3. 가능하면 네가 작성한 코드를 다시 검토하고 오류가 있다면 나에게 알리고 수정하라.
4. 위와 별개로 논리적 오류에 대해서는 이유를 나에게 알려라.

</할 일>

<기타>

1. 관리자 페이지의 경우 내부망에서만 접근 가능하도록 설정할 예정이다. 그러므로 기본적인 id, pw만 간단하게 검증하고 그 이상은 하지 않겠다.
2. MariaDB 접속 정보
    * host: localhost
    * port: 3306
    * username: root
    * password: root

</기타>