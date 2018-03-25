<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="昵称" clearable></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getFriends">查询</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="users" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column type="index" width="60">
			</el-table-column>
			<el-table-column prop="avatar" width="80" label="头像">
				<template slot-scope="scope">
					<img :src="formatAvatar(scope.row)" class="avatar"/>
				</template>
			</el-table-column>
			<el-table-column prop="nick_name" label="昵称" min-width="100" sortable show-overflow-tooltip>
			</el-table-column>
			<el-table-column prop="remark_name" label="备注名" min-width="100" sortable show-overflow-tooltip>
			</el-table-column>
			<el-table-column prop="sex" label="性别" min-width="70" :formatter="formatSex" sortable>
			</el-table-column>
			<el-table-column prop="province" label="省份" min-width="70" sortable>
			</el-table-column>
			<el-table-column prop="city" label="城市" width="100" sortable>
			</el-table-column>
			<el-table-column prop="signature" label="个性签名" min-width="200" sortable show-overflow-tooltip>
			</el-table-column>
			<el-table-column label="操作" min-width="150">
				<template slot-scope="scope">
					<el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
					<el-button type="primary" size="small" @click="handleMsg(scope.row)">发消息</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<!--<el-button type="primary" @click="batchMessage" :disabled="this.sels.length===0">发消息</el-button>-->
			<!--<el-button type="primary" @click="handleMsg(null)" :disabled="this.sels.length===0">群发消息</el-button>-->
			<el-button type="primary" @click="batchMessage" :disabled="this.sels.length===0">群发消息</el-button>
			<el-pagination background layout="prev, pager, next" @size-change="handleSizeChange" @current-change="handleCurrentChange" :page-size="pageSize" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--好友编辑界面-->
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="昵称" prop="nick_name">
					<el-input v-model="editForm.nick_name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="备注名">
					<el-input v-model="editForm.remark_name" auto-complete="off"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="editFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
			</div>
		</el-dialog>

		<!--消息编辑界面-->
		<el-dialog title="发送消息" v-model="msgFormVisible" :close-on-click-modal="false">
			<el-form :model="msgForm" label-width="80px" :rules="msgFormRules" ref="msgForm">
				<el-form-item label="发消息给" prop="nick_name">
					<!--<el-input v-model="msgForm.nick_name" auto-complete="off"></el-input>-->
					{{ msgForm.nick_name }}
				</el-form-item>
				<el-form-item label="消息">
					<el-input type="textarea" v-model="msgForm.content" auto-complete="off"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="msgFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="msgSubmit" :loading="msgFormLoading">发送</el-button>
			</div>
		</el-dialog>

	</section>
</template>

<script>
	import util from '../../common/js/util'
	//import NProgress from 'nprogress'
	import { getFriendListPage, editFriend, sendMessage, batchSendMessage } from '../../api/api';

	export default {
		data() {
			return {
				filters: {
					name: ''
				},
				users: [],
				total: 0,
				page: 1,
				pageSize: 10,
				listLoading: false,
				sels: [],//列表选中列
				editFormVisible: false,//编辑界面是否显示
				editLoading: false,
				editFormRules: {
					nick_name: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
				},
				//编辑界面数据
				editForm: {
					id: 0,
					puid: '',
					nick_name: '',
					remark_name: ''
				},
                msgFormVisible: false,
                msgFormLoading: false,
                msgFormRules: {
                    message: [{ required: true, message: '请输入消息内容', trigger: 'blur'}]
                },
				msgForm: {
                    sender_id: JSON.parse(sessionStorage.getItem('user')).puid,
                    receiver_id: '',
                    group_id: null,
                    content: '',
                    type: 1 // 'text'
				}
			}
		},
		methods: {
            formatSex: function(row) {
                return row.sex == 1 ? '男' : row.sex == 2? '女' : '';
			},
			formatAvatar: function(row) {
              	return  "http://localhost:8000" + row.avatar;
			},
            handleSizeChange(val) {
                this.pageSize = val;
			},
			handleCurrentChange(val) {
				this.page = val;
				this.getFriends();
			},
			//获取用户列表
			getFriends() {
				let para = {
					page: this.page,
					page_size: this.pageSize,
                    nick_name__contains: this.filters.name
				};
				this.listLoading = true;
				//NProgress.start();
				getFriendListPage(para).then((res) => {
				    console.log("get page data");
				    console.log(para);
				    console.log(res);
					this.total = res.data.count;
					this.users = res.data.results;
					this.listLoading = false;
				});
			},
			//显示编辑界面
			handleEdit: function (row) {
                console.log(this.editForm);
				// this.editForm = Object.assign({}, row);
                // this.editForm.id = row.id;
                this.editForm.puid = row.puid;
				this.editForm.nick_name = row.nick_name;
				this.editForm.remark_name = row.remark_name;
                this.editFormVisible = true;
			},
			//编辑
			editSubmit: function () {
				this.$refs.editForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.editLoading = true;
							let para = Object.assign({}, this.editForm);
                            console.log('Edit user info parameters:');
							console.log(para);
							editFriend(para).then((res) => {
							    console.log('Response from server:');
							    console.log(res);

                                if (res.status<400) {
                                    this.editLoading = false;
                                    this.$message({
                                        message: '提交成功',
                                        type: 'success',
                                        showClose: true
                                    });
                                    this.$refs['editForm'].resetFields();
                                    this.editFormVisible = false;
                                    this.getFriends();
								}
                                else {
                                    this.editLoading = false;
                                    this.$message({
                                        message: res.data,
                                        type: 'error',
                                        showClose: true
                                    });
								}

							});
						});
					}
				});
			},
            handleMsg: function(row) {
                if (row) {
                    this.msgForm.receiver_id = row.puid;
                    this.msgForm.nick_name = row.nick_name;
				}
				else {
                    this.msgForm.receiver_id = this.sels.map(item => item.puid);
                    this.msgForm.nick_name = this.sels.map(item => item.nick_name).toString();
				}

                this.msgForm.content = '';
                this.msgFormVisible = true;
            },
			msgSubmit: function () {
                this.$refs.msgForm.validate((valid) => {
                    if (valid) {
                        this.msgFormLoading = true;
                        let para = Object.assign({}, this.msgForm);
						console.log('Send message parameters:');

						if (typeof(para.receiver_id) == 'string'){
                            console.log(para);
                            console.log(typeof(para.receiver_id));
                            sendMessage(para).then((res) => {
                                console.log('Response from server:');
                                console.log(res);

                                if (res.status<400) {
                                    this.msgFormLoading = false;
                                    this.$message({
                                        message: '发送成功',
                                        type: 'success',
                                        showClose: true
                                    });
                                    this.$refs['msgForm'].resetFields();
                                    this.msgFormVisible = false;
                                    this.getFriends();
                                }
                                else {
                                    this.msgFormLoading = false;
                                    this.$message({
                                        message: res.data,
                                        type: 'error',
                                        showClose: true
                                    });
                                }
                            });
						}
						else {
                            let para_list = new Array();
                            for (var i in this.msgForm.receiver_id) {
                                let new_para = {
                                    // 'to_type': this.msgForm.to_type,
                                    'receiver_id': this.msgForm.receiver_id[i],
                                    'sender_id': this.msgForm.sender_id,
									'group_id': this.msgForm.group_id,
									'content': this.msgForm.content,
									'type': this.msgForm.type
                                };
                                para_list.push(new_para);
                                console.log(para_list);
								// batchSendMessage(para_list).then((res) => {
								batchSendMessage(para_list).then((res) => {
                                    // console.log('Response from server:');
                                    // console.log(res);

                                    // if (res.status<400) {
                                        this.msgFormLoading = false;
                                        this.$message({
                                            message: '发送成功',
                                            type: 'success',
                                            showClose: true
                                        });
                                        this.$refs['msgForm'].resetFields();
                                        this.msgFormVisible = false;
                                        this.getFriends();
                                    // }
                                    // else {
                                    //     this.msgFormLoading = false;
                                    //     this.$message({
                                    //         message: res.data,
                                    //         type: 'error',
                                    //         showClose: true
                                    //     });
                                    // }
								});
                            }
						};

                    }
                });
			},
			selsChange: function (sels) {
				this.sels = sels;
			},
			batchMessage: function () {
                var ids = this.sels.map(item => item.puid).toString();
                this.$router.push({
						path: '/send_msg/contact',
						// query: { ids: ids, type: this.queryType, gid: this.gid || '' }
						query: { ids: ids, type: 'contact', gid: '' }
                })
			},
		},
		mounted() {
			this.getFriends();
		}
	}

</script>

<style scoped>
	.avatar {
		width: 30px;
		height: 30px;
		/*border-radius: 20px;*/
		border-radius: 5px;
		margin: 5px 0px 0px 0px;
	}
</style>