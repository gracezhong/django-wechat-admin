<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="姓名" clearable></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getgroups">查询</el-button>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="groups" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column type="index" width="60">
			</el-table-column>
			<el-table-column prop="avatar" width="80">
				<template slot-scope="scope">
					<img :src="formatAvatar(scope.row)" class="avatar"/>
				</template>
			</el-table-column>
			<el-table-column prop="nick_name" label="昵称" width="300" sortable>
			</el-table-column>
			<el-table-column prop="owner" label="群主" width="160">
				<template slot-scope="scope">
					<div v-if="!isEmptyObject(scope.row.owner)">
						<img :src="formatAvatar(scope.row.owner)" class="avatar" v-if="scope.row.owner.avatar"/>
						<!--<a href="#" class="nick-name">{{scope.row.sender.nick_name}}</a>-->
						{{scope.row.owner.nick_name}}
					</div>
				</template>
			</el-table-column>

			<el-table-column label="操作" min-width="150">
				<template slot-scope="scope">
					<el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
			<el-pagination background layout="prev, pager, next" @size-change="handleSizeChange" @current-change="handleCurrentChange" :page-size="pageSize" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--编辑界面-->
		<el-dialog title="编辑" v-model="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="80px" :rules="editFormRules" ref="editForm">
				<el-form-item label="用户名" prop="nick_name">
					<el-input v-model="editForm.nick_name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="密码" prop="password">
					<el-input type="password" v-model="editForm.password" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="员工">
					<el-radio-group v-model="editForm.is_staff">
						<el-radio class="radio" :label="true">是</el-radio>
						<el-radio class="radio" :label="false">否</el-radio>
					</el-radio-group>
				</el-form-item>
				<el-form-item label="邮箱">
					<el-input v-model="editForm.email" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="手机">
					<el-input v-model="editForm.phone" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="自我介绍">
					<el-input type="textarea" v-model="editForm.description"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="editFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
			</div>
		</el-dialog>

		<!--新增界面-->
		<el-dialog title="新增" v-model="addFormVisible" :close-on-click-modal="false">
			<el-form :model="addForm" label-width="80px" :rules="addFormRules" ref="addForm">
				<el-form-item label="用户名" prop="nick_name">
					<el-input v-model="addForm.nick_name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="密码" prop="password">
					<el-input type="password" v-model="addForm.password" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="员工">
					<el-radio-group v-model="addForm.is_staff">
						<el-radio class="radio" :label="1">是</el-radio>
						<el-radio class="radio" :label="0">否</el-radio>
					</el-radio-group>
				</el-form-item>
				<el-form-item label="邮箱">
					<el-input v-model="addForm.email" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="手机">
					<el-input v-model="addForm.phone" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="自我介绍">
					<el-input type="textarea" v-model="addForm.description"></el-input>
				</el-form-item>
			</el-form>
			<div slot="footer" class="dialog-footer">
				<el-button @click.native="addFormVisible = false">取消</el-button>
				<el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
			</div>
		</el-dialog>
	</section>
</template>

<script>
	import util from '../../common/js/util'
	//import NProgress from 'nprogress'
	import { getGroupListPage } from '../../api/api';

	export default {
		data() {
			return {
				filters: {
					name: ''
				},
				groups: [],
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
					nick_name: '',
					is_staff: -1,
					email: null,
					description: null,
					phone: null
				},

				addFormVisible: false,//新增界面是否显示
				addLoading: false,
				addFormRules: {
					nick_name: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
				},
				//新增界面数据
				addForm: {
                    nick_name: '',
                    is_staff: -1,
                    email: null,
                    description: null,
                    phone: null
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
            formatAvatar: function(row) {
                return  "http://localhost:8000" + row.avatar;
            },
            handleSizeChange(val) {
                this.pageSize = val;
			},
			handleCurrentChange(val) {
				this.page = val;
				this.getgroups();
			},
			//获取用户列表
			getgroups() {
				let para = {
					page: this.page,
					page_size: this.pageSize,
                    nick_name__contains: this.filters.name
				};
				this.listLoading = true;
				//NProgress.start();
				getGroupListPage(para).then((res) => {
				    console.log("get page data");
				    console.log(para);
				    console.log(res);
					this.total = res.data.count;
					this.groups = res.data.results;
					this.listLoading = false;
					//NProgress.done();
				});
			},
			//删除
			handleDel: function (index, row) {
				this.$confirm('确认删除该记录吗?', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					//NProgress.start();
					let para = { id: row.id };
					removeUser(para).then((res) => {
						this.listLoading = false;
						console.log(res);
						//NProgress.done();
						this.$message({
							message: '删除成功',
							type: 'success'
						});
						this.getgroups();
					});
				}).catch(() => {

				});
			},
			//显示编辑界面
			handleEdit: function (index, row) {
                console.log(this.editForm);
				// this.editForm = Object.assign({}, row);
                this.editForm.puid = row.puid;
				this.editForm.nick_name = row.nick_name;
				this.editForm.email = row.email;
				this.editForm.description = row.description;
				this.editForm.phone = row.phone;
				// console.log(this.editForm);
                this.editFormVisible = true;
			},
			//显示新增界面
			handleAdd: function () {
				// this.addForm = {
                 //    nick_name: '',
                 //    email: null,
                 //    description: null,
                 //    phone: null
				// };
                this.addFormVisible = true;
			},
			//编辑
			editSubmit: function () {
				this.$refs.editForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.editLoading = true;
							//NProgress.start();
							let para = Object.assign({}, this.editForm);
							// console.log(this.editForm);
                            console.log('Edit user info parameters:');
							console.log(para);
							editUser(para).then((res) => {
							    console.log('Response from server:');
							    console.log(res);

                                if (res.status<400) {
                                    this.editLoading = false;
                                    //NProgress.done();
                                    this.$message({
                                        message: '提交成功',
                                        type: 'success',
                                        showClose: true
                                    });
                                    this.$refs['editForm'].resetFields();
                                    this.editFormVisible = false;
                                    this.getgroups();
								}
                                else {
                                    this.editLoading = false;
                                    //NProgress.done();
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
			//新增
			addSubmit: function () {
				this.$refs.addForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.addLoading = true;
							//NProgress.start();
							let para = Object.assign({}, this.addForm);
							console.log('Add new user');
							console.log(para);
							// para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');
							addUser(para).then((res) => {
							    console.log(res);
							    if (res.errors) {
                                    this.addLoading = false;
							        this.$message( {
										message: res.errors,
										type: 'error'
									});
								}
								else {
							        console.log('User is added successfully.');
							        console.log(res);
                                    this.addLoading = false;
                                    //NProgress.done();
                                    this.$message({
                                        message: '提交成功',
                                        type: 'success'
                                    });
                                    this.$refs['addForm'].resetFields();
                                    this.addFormVisible = false;
                                    this.getgroups();
								}

							});
						});
					}
				});
			},
			selsChange: function (sels) {
				this.sels = sels;
			},
			//批量删除
			batchRemove: function () {
				var ids = this.sels.map(item => item.id).toString();
				this.$confirm('确认删除选中记录吗？', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					//NProgress.start();
					let para = { ids: ids };
					console.log(para.ids);
					batchRemoveUser(para).then((res) => {
						this.listLoading = false;
						//NProgress.done();
						this.$message({
							message: '删除成功',
							type: 'success'
						});
						this.getgroups();
					});
				}).catch(() => {

				});
			}
		},
		mounted() {
			this.getgroups();
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
</style>