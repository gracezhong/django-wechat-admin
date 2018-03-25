<!--<template>-->
  <!--<el-form :model="ruleForm2" :rules="rules2" ref="ruleForm2" label-position="left" label-width="0px" class="demo-ruleForm login-container">-->
    <!--<h3 class="title">系统登录</h3>-->
    <!--<el-form-item prop="account">-->
      <!--<el-input type="text" v-model="ruleForm2.account" auto-complete="off" placeholder="账号"></el-input>-->
    <!--</el-form-item>-->
    <!--<el-form-item prop="checkPass">-->
      <!--<el-input type="password" v-model="ruleForm2.checkPass" auto-complete="off" placeholder="密码"></el-input>-->
    <!--</el-form-item>-->
    <!--<el-checkbox v-model="checked" checked class="remember">记住密码</el-checkbox>-->
    <!--<el-form-item style="width:100%;">-->
      <!--<el-button @click.native.prevent="wechatLogin" :loading="logining">微信登录</el-button>-->
      <!--&lt;!&ndash;<el-button @click.native.prevent="handleReset2">重置</el-button>&ndash;&gt;-->
    <!--</el-form-item>-->
  <!--</el-form>-->
<!--</template>-->

<!--<script>-->
  <!--import { normalLogin, wechatLogin } from '../api/api';-->
  <!--import ElFormItem from "element-ui/packages/form/src/form-item";-->
  <!--//import NProgress from 'nprogress'-->
  <!--export default {-->
      <!--components: {ElFormItem},-->
      <!--data() {-->
      <!--return {-->
        <!--logining: false,-->
        <!--ruleForm2: {-->
          <!--account: 'grace',-->
          <!--checkPass: 'grace@1234'-->
        <!--},-->
        <!--rules2: {-->
          <!--account: [-->
            <!--{ required: true, message: '请输入账号', trigger: 'blur' },-->
            <!--//{ validator: validaePass }-->
          <!--],-->
          <!--checkPass: [-->
            <!--{ required: true, message: '请输入密码', trigger: 'blur' },-->
            <!--//{ validator: validaePass2 }-->
          <!--]-->
        <!--},-->
        <!--checked: true-->
      <!--};-->
    <!--},-->
    <!--methods: {-->
      <!--handleReset2() {-->
        <!--this.$refs.ruleForm2.resetFields();-->
      <!--},-->
        <!--wechatLogin(){-->
          <!--this.eventSource = this.$eventSourceListener('test');-->
          <!--wechatLogin().then(res => {-->
              <!--console.log(res);-->
              <!--this.logining = true;-->
              <!--let user = res.data;-->
              <!--console.log(JSON.stringify(user));-->
              <!--try {-->
                  <!--sessionStorage.setItem('user', JSON.stringify(user));-->
              <!--}-->
              <!--catch(err){-->
                  <!--console.log(err);-->
              <!--}-->
              <!--console.log(user.puid);-->
              <!--console.log('User is logged in');-->
              <!--this.eventSource.close();-->
              <!--this.$router.push({ path: '/friendlist' });-->
          <!--})-->
        <!--}-->
    <!--}-->
  <!--}-->

<!--</script>-->

<!--<style lang="scss" scoped>-->
  <!--.login-container {-->
    <!--/*box-shadow: 0 0px 8px 0 rgba(0, 0, 0, 0.06), 0 1px 0px 0 rgba(0, 0, 0, 0.02);*/-->
    <!-- -webkit-border-radius: 5px;-->
    <!--border-radius: 5px;-->
    <!-- -moz-border-radius: 5px;-->
    <!--background-clip: padding-box;-->
    <!--margin: 180px auto;-->
    <!--width: 350px;-->
    <!--padding: 35px 35px 15px 35px;-->
    <!--background: #fff;-->
    <!--border: 1px solid #eaeaea;-->
    <!--box-shadow: 0 0 25px #cac6c6;-->
    <!--.title {-->
      <!--margin: 0px auto 40px auto;-->
      <!--text-align: center;-->
      <!--color: #505458;-->
    <!--}-->
    <!--.remember {-->
      <!--margin: 0px 0px 35px 0px;-->
    <!--}-->
  <!--}-->
<!--</style>-->


<template>
  <div class="body">
    <div class="login">
      <div class="login_box">
        <div class="qrcode">
          <img class="img" :src="this.qrCode">
          <div>
            <p class="sub_title">{{sub_title}}</p>
            <p class="sub_desc">{{sub_desc}}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
    import { Login } from '../api/api';
    export default {
        methods: {
            // validate(res) {
            //     console.log(res);
            //     // let { msg, r } = res.data;
            //     // if (r !== 0) {
            //     //     this.$message({
            //     //         message: msg,
            //     //         type: 'error'
            //     //     });
            //     //     return false;
            //     // }
            //     return true;
            // },
            login() {
                this.eventSource = this.$eventSourceListener();
                Login().then(res => {
                    console.log(res);
                    // this.validate(res);
                    this.eventSource.close();
                });
            }
        },
        mounted() {
            this.login();
        }
    }
</script>

<style lang="scss">
  body, dd, dl, fieldset, h1, h2, h3, h4, h5, h6, ol, p, textarea, ul {
    margin: 0;
  }
  a, button, input, textarea {
    outline: 0;
  }

  body, html {
    height: 100%;
  }

  body {
    line-height: 1.6;
    font-family: Helvetica Neue,Helvetica,Hiragino Sans GB,Microsoft YaHei,\\5FAE\8F6F\96C5\9ED1,Arial,sans-serif;
    //    background: url(../assets/bg2.jpg) no-repeat 50%;
    //    background-size: cover;
  }

  .login {
    height: 100%;
    min-width: 860px;
    min-height: 700px;
    overflow: auto;
    position: relative;
  }

  .login_box {
    position: absolute;
    top: 50%;
    left: 50%;
    margin-left: -190px;
    margin-top: -270px;
    border-radius: 4px;
    -moz-border-radius: 4px;
    -webkit-border-radius: 4px;
    background-color: #fff;
    width: 380px;
    height: 540px;
    shadow: 0 2px 10px #999;
    .qrcode {
      position: relative;
      text-align: center;
      .img {
        display: block;
        width: 270px;
        height: 270px;
        margin: 42px auto 12px;
      }
      .sub_title {
        text-align: center;
        font-size: 20px;
        color: #353535;
        margin-bottom: 20px;
      }
      .sub_desc {
        text-align: center;
        color: #888;
        font-size: 18px;
      }
    }
  }
</style>
