<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.content" placeholder="消息内容" clearable></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getMsgs">查询</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="msgs" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" min-width="55">
			</el-table-column>
			<el-table-column prop="group" label="群聊" min-width="160">
				<template slot-scope="scope">
					<div v-if="!isEmptyObject(scope.row.group)">
						<img :src="formatAvatar(scope.row.group)" class="avatar" v-if="scope.row.group.avatar"/>
						{{scope.row.group.nick_name}}
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="sender" label="发送者" min-width="160">
				<template slot-scope="scope">
					<div v-if="!isEmptyObject(scope.row.sender)">
						<img :src="formatAvatar(scope.row.sender)" class="avatar" v-if="scope.row.sender.avatar"/>
						{{scope.row.sender.nick_name}}
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="content" label="内容" min-width="400" sortable>
				<template slot-scope="scope">
					<div v-if="scope.row.url">
						<a :href="scope.row.url" target="_blank" class="content">{{scope.row.content}}</a>
					</div>
					<!-- Picture-->
					<div v-else-if="scope.row.type == 6">
						<img :src="formatSource(scope.row)" class="picture"/>
					</div>
					<!-- Recording -->
					<div v-else-if="scope.row.type == 7">
						<audio controls="controls"><source :src="formatSource(scope.row)" /></audio>
					</div>
					<!-- Video-->
					<div v-else-if="scope.row.type == 9">
						<video controls="controls" :src="formatSource(scope.row)" class="video"></video>
					</div>
					<!-- Card and other types of message-->
					<div v-else>{{ scope.row.type == 3 ? '名片：' : '' }} {{scope.row.content}}</div>
				</template>
			</el-table-column>
			<el-table-column prop="receive_time" label="时间" min-width="180" sortable show-overflow-tooltip>
			</el-table-column>
			<el-table-column label="操作" min-width="150">
				<template slot-scope="scope">
					<el-button type="primary" size="small" @click="handleMsg(scope.row)">回复</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-pagination background layout="prev, pager, next" @size-change="handleSizeChange" @current-change="handleCurrentChange" :page-size="pageSize" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--消息编辑界面-->
		<el-dialog title="发送消息" v-model="msgFormVisible" :close-on-click-modal="false">
			<el-form :model="msgForm" label-width="80px" :rules="msgFormRules" ref="msgForm">
				<el-form-item label="发消息给" prop="nick_name">
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
	import { getMsgListPage, sendMessage } from '../../api/api';

	export default {
		data() {
			return {
				filters: {
					content: ''
				},
				msgs: [],
				total: 0,
				page: 1,
				pageSize: 20,
				listLoading: false,
				sels: [],//列表选中列
                msgFormVisible: false,
                msgFormLoading: false,
                msgFormRules: {
                    content: [{ required: true, content: '请输入消息内容', trigger: 'blur'}]
                },
                msgForm: {
					sender_id: '',
					receiver_id: '',
                    content: '',
                    type: 1 // text
                }
			}
		},
		methods: {
            isEmptyObject( obj ) {
                for ( var name in obj ) {
                    return false;
                }
                return true;
            },
            formatSource: function(row) {
                // console.log(row.file_ext);
                return 'http://localhost:8000/static/msg_uploads/' + row.id + row.file_ext;
            },
            handleSizeChange(val) {
                this.pageSize = val;
			},
			handleCurrentChange(val) {
				this.page = val;
				this.getMsgs();
			},
            formatAvatar: function(obj) {
                // console.log(row);
                return  "http://localhost:8000" + obj.avatar;
            },
            formatSender(sender) {
                console.log(sender.nick_name);
                return sender.nick_name;
                if (sender.name) {

				}
			},
			//获取接收消息列表
			getMsgs() {
                let user = sessionStorage.getItem('user');
                user = JSON.parse(user);
                console.log(user);
				let para = {
					page: this.page,
					page_size: this.pageSize,
                    content__contains: this.filters.content,
                    receiver_id: user.puid
				};
                console.log(para);
				this.listLoading = true;
				getMsgListPage(para).then((res) => {
				    console.log("get page data");
				    console.log(res);
					this.total = res.data.count;
					this.msgs = res.data.results;
					console.log(this.msgs);
					this.listLoading = false;
				});
			},
			selsChange: function (sels) {
				this.sels = sels;
			},
            handleMsg: function(row) {
                // console.log(row.group);
                // console.log(row.sender);
                if (row.group) {
                    this.msgForm.group_id = row.group.puid;
                    // this.msgForm.receiver = row.group;
                    // this.msgForm.to_type = 'group';
				}
				else{
                    // this.msgForm.receiver = row.sender;
                    this.msgForm.group_id = null;
                    // this.msgForm.to_type = 'friend';
				}
				this.msgForm.sender_id = row.receiver.puid;
                this.msgForm.receiver_id = row.sender.puid;
                this.msgForm.nick_name = row.sender.nick_name;
                this.msgForm.content = '';
                this.msgFormVisible = true;
            },
            msgSubmit: function () {
                this.$refs.msgForm.validate((valid) => {
                    if (valid) {
                        this.msgFormLoading = true;
                        let para = Object.assign({}, this.msgForm);
                        console.log('Send message parameters:');
                        console.log(para);
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
                                this.getMsgs();
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
                });
            },
		},
		mounted() {
			this.getMsgs();
		}
	}

</script>

<style scoped>
	.avatar {
		width: 40px;
		height: 40px;
		border-radius: 5px;
		margin: 10px 0px 5px 0px;
	}
	.picture {
		max-height: 120px;
	}
	.video {
		max-width: 160px;
	}
</style>