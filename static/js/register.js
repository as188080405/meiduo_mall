var vm = new Vue({
    el: '#app',
    // 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[',']]'],
    data: {
        //接收参数
        username:'',
        password:'',
        password2:'',
        mobile:'',
        allow:'',
        image_code:'',
        image_code_url:'',
        sms_code:'',
        sms_code_tip:'',
        sms_falg:false,
        //提示标记
        error_username:false,
        error_password:false,
        error_confirm:false,
        error_mobile:false,
        error_allow:false,
        error_image_code:false,
        error_sms_code:false,
        //错误信息展示
        sms_code_tip: '获取短信验证码',
        error_username_message:'',
        error_password_message:'',
        error_confirm_message:'',
        error_mobile_message:'',
        error_captcha_message:'',
        error_allow_message:'',
        error_image_code_message:'',
        error_sms_code_message:'',
    },
    mounted:function(){
        this.generate_image_code();
    },
    methods:{
        // 发送短信验证码
        sms_send_code:function(){
            if (this.sms_falg == true){
                return;
            }
            this.check_mobile();
            this.check_image_code();
            let url = "/sms_codes/" + this.mobile + "?image_code=" + this.image_code + "&uuid=" + this.uuid;
            axios.get(url).then(response=>{
                if(response.data.code == 0){
                    let num = 60;
                    let t = setInterval(()=>{
                        if (num == 1){
                            clearInterval(t);
                            this.sms_code_tip = '请输入短信验证码';
                            this.sms_falg = false;
                        }else{
                            num -= 1;
                            this.sms_code_tip = num + "秒";
                        }
                    }, 1000, 60);
                }else{
                    if (response.data.code == 4001){
                        this.error_image_code_message = resposne.data.errmsg;
                        this.error_image_code = true;
                    }else{
                        this.error_sms_code_message = resposne.data.errmsg;
                        this.error_sms_code = true;
                    }
                    this.generate_image_code();
                    this.sms_falg = false;
                }
            }).catch(error=>{
                console.log(error.response);
                this.sms_falg = false;
            })
        },
        // 获取图片验证码
        generate_image_code:function(){
            // 获取uuid，生成uuid的函数封装在common,js中
            this.uuid = generateUUID()
            // 拼接后端获取图片验证码的url
            this.image_code_url = "/image_codes/" + this.uuid + "/"
        },
        // 检测用户名
        check_username:function(){
            let re = /^[a-zA-Z0-9_]{5,20}$/
            if(re.test(this.username) & this.username != ""){
                this.error_username = false
                //  验证用户名是否重复
                let url = "/usernames/" + this.username + "/count/"
                axios.get(url).then(response=>{
                    if(response.data.count == 0){
                        this.error_username = false
                    }else{
                        this.error_username = true
                        this.error_username_message = "用户名已存在！"
                    }
                }).catch(error=>{
                    alert(error.data.errmsg)
                })
            }else{
                this.error_username_message = "亲，用户名必须使用5-20个数字/字母/下划线！"
                this.error_username = true
            }
        },
        // 检测密码
        check_password:function(){
            let re = /^[a-zA-Z0-9]{5,20}$/
            if(re.test(this.password)){
                this.error_password = false
            }else{
                this.error_password_message = '亲，密码必须使用5-20个字母/数字！'
                this.error_password = true
            }
        },
        // 检测确认密码
        check_confirm_password:function(){
            if(this.password2 != this.password){
                this.error_confirm_message = '老铁，两次输入的密码不一致！'
                this.error_confirm = true
            }else{
                this.error_confirm = false
            }
        },
        // 检验验证码
        check_image_code:function() {
            let re = /^[a-zA-Z0-9]{4}$/;
            if(re.test(this.image_code)){
                this.error_image_code=false;
            }else{
                this.error_image_code=true;
                this.error_image_code_message='请输入正确的图片验证码';
            }
        },
        // 检测手机号
        check_mobile:function() {
            let re = /^1[3-9]\d{9}$/;
            if(re.test(this.mobile) & this.mobile != ""){
                this.error_mobile=false;
                // 验证手机号码是否重复
                let url = "/mobile/" + this.mobile + "/count/"
                axios.get(url).then(response=>{
                    if(response.data.count == 0){
                        this.error_mobile = false
                    }else{
                        this.error_mobile = true
                        this.error_mobile_message = "手机号码已注册"
                    }
                }).catch(error=>{
                    alert(error.data.errmsg)
                })
            }else{
                this.error_mobile=true;
                this.error_mobile_message='请输入正确的手机号码';
            }
        },
        // 检测短信验证码
        check_sms_code:function(){
            let re = /1[3-9]\d{9}/
            if (re.test(this.sms_code)){
                this.error_sms_code = false
            }else{
                this.error_sms_code_message = '验证码仅限6位数字'
                this.error_sms_code = true
            }
        },
        // 提交注册按钮
        on_submit:function () {

            this.check_username();
            this.check_password();
            this.check_confirm_password();
            this.check_mobile();

            if(this.error_username==true||this.error_password==true||this.error_confirm==true||this.error_mobile==true){
                window.event.returnValue=false;
            }

        },
    },
});


