import React, {useState} from 'react'
import {login as authLogin} from '../../store/authSlice'
import {useDispatch} from 'react-redux'
import {useForm} from 'react-hook-form'
import authService from '../../appwrite/auth'
import {Link,useNavigate} from 'react-router-dom'

import Input from '../../components/input/Input'
import Button from '../../components/button/Button'

import './style.scss'

const Signup = () => {
  const navigate = useNavigate()
    const dispatch = useDispatch()
    const {register, handleSubmit} = useForm()
    const [error, setError] = useState("");

    const create = async(data) => {
        setError("")
        try {
            const createdUser = await authService.createAccount(data)
            if (createdUser){
                const session = await authService.login({email: data.email, password: data.password})
                if(session){
                    dispatch(authLogin(session));
                    navigate("/")
                }
            }
        } catch (error) {
            setError(error.message)
            console.log(error)
        }
    }
  return (
    <div className='myContainer'>
      <div className='myCard'>
        <h2>Sign Up </h2>
        
        <form onSubmit={handleSubmit(create)}>
            <div className='formContainer'>
                <Input
                    label="Full name:"
                    placeholder="Enter your full name"
                    maxLength={40}
                    {...register("name", {
                        required: true,
                        maxLength: 40
                    })}
                />
                <Input 
                label="Email"
                placeholder="Enter your email"
                type="email"
                {...register("email",
                    {required:true,
                    maxLength:40,
                    validate:{
                        matchPatern: (value) => /^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/.test(value) ||
                        "Email address must be a valid address",
                    }})
                }/>
                <Input
                label="Password: "
                type="password"
                placeholder="Enter your password"
                {...register("password",{
                    required:true,
                })}
                />
                {error && <p className='error'>{error}</p>}
                <Button type="submit" className='myBtn'>Sign Up</Button>
            </div>
        </form>
        <p className='toNav'>Already have an account? <Link to="/login" className='navBtn'>Log In</Link></p>
      </div>
    </div>
  )
}

export default Signup
