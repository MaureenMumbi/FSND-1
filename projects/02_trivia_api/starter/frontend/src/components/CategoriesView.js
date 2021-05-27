import React,{ Component } from "react";
import $ from 'jquery';

import '../stylesheets/CategoriesView.css'

class CategoriesView extends Component{
    constructor(props){
        super();
        this.state={
            type:""
        }
    }

submitCategory = (event) => {
    event.preventDefault();
    $.ajax({
        url:"categories",
        type:"POST",
        dataType:"json",
        contentType:"application/json",
        data: JSON.stringify({
            type: this.state.type
        }),
        xhrFields:{
            withCredentials:true
        },
        crossDomain:true,
        success: (result)=>{
            document.getElementById('add-category-form').reset();
            return;
        },
        error:result => {
            alert("Unable to add a category, Please try your request again")
        }
    })
}
handleChange = (event)=>{
    this.setState({[event.target.name]: event.target.value})
}

render(){
    return(

        <div id="add-form">
           <h2>Add a new category</h2> 
           <form className="form-view" id="add-category-form" onSubmit={this.submitCategory}>
                <label>Type
                    <input type="text" name="type" onChange={this.handleChange}/>
                </label>
                <input type="submit" className="button" value="Submit" />
           </form>
        </div>
    );
}
}
export default CategoriesView;

